"""
Quiz generation using LangChain and Groq LLM.
Uses Groq free tier API (no credit card required).
"""
import json
import re
from collections import Counter
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..config import get_settings
from ..prompts.quiz_prompts import QUIZ_GENERATION_PROMPT


class QuizGenerator:
    """Generates quiz from Wikipedia article content using LLM."""
    
    def __init__(self):
        settings = get_settings()
        self.mock_mode = False
        self.llm: Optional[ChatGroq] = None

        if not settings.GROQ_API_KEY:
            if settings.REQUIRE_GROQ_API_KEY:
                raise ValueError(
                    "GROQ_API_KEY is required. Get a free API key (no card needed) from "
                    "https://console.groq.com/keys"
                )
            self.mock_mode = True
            return

        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.3,  # Lower temp for factual output
        )
    
    def generate_quiz(self, title: str, sections: list, content: str) -> dict:
        """
        Generate quiz and related topics from article content.
        Returns dict with 'quiz' (list of question dicts) and 'related_topics'.
        """
        if self.mock_mode or not self.llm:
            return self._generate_mock_quiz(title=title, sections=sections, content=content)

        prompt = ChatPromptTemplate.from_template(QUIZ_GENERATION_PROMPT)
        chain = prompt | self.llm | StrOutputParser()
        
        sections_str = ", ".join(sections) if sections else "Introduction"
        
        response = chain.invoke({
            "title": title,
            "sections": sections_str,
            "content": content,
        })
        
        return self._parse_llm_response(response, title)

    def _generate_mock_quiz(self, title: str, sections: list, content: str) -> dict:
        """
        Heuristic fallback generator (no API key required).
        This is intentionally simple: it creates a small quiz based on "X is/was Y" facts
        found in the scraped article content.
        """
        # Sentence split (lightweight)
        text = re.sub(r"\s+", " ", (content or "")).strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if 40 <= len(s.strip()) <= 220]

        # Extract simple "subject is/was ..." facts
        fact_pattern = re.compile(r"^([A-Z][A-Za-z0-9 ,.'()-]{2,60})\s+(is|was|are|were)\s+(.+?)\.$")
        def _clean_subject(s: str) -> str:
            s = (s or "").strip()
            for prefix in ("The ", "A ", "An "):
                if s.startswith(prefix):
                    return s[len(prefix) :].strip()
            return s

        facts = []
        for s in sentences[:80]:
            m = fact_pattern.match(s)
            if not m:
                continue
            subject = _clean_subject(m.group(1).strip())
            verb = m.group(2).strip()
            obj = m.group(3).strip()
            if len(subject) < 3 or len(obj) < 10:
                continue
            # Avoid super generic subjects
            if subject.lower() in {"it", "this", "he", "she", "they"}:
                continue
            facts.append((subject, verb, obj))
            if len(facts) >= 10:
                break

        # Build options using other objects as distractors
        objects = [o for _, _, o in facts]

        quiz = []
        for i, (subj, verb, obj) in enumerate(facts[:8]):
            distractors = [o for o in objects if o != obj][:3]
            # Pad distractors from other sentences if needed
            if len(distractors) < 3:
                for s in sentences[80:120]:
                    if s.endswith(".") and s[:-1] != obj and len(s) < 120:
                        distractors.append(s[:-1])
                    if len(distractors) >= 3:
                        break
            options = [obj] + distractors[:3]
            # Deterministic shuffle: rotate by i
            rot = i % len(options) if options else 0
            options = options[rot:] + options[:rot]
            answer = obj
            quiz.append(
                {
                    "question": f"According to the article, what {verb} {subj}?",
                    "options": options[:4],
                    "answer": answer,
                    "difficulty": "easy" if i < 3 else ("medium" if i < 6 else "hard"),
                    "explanation": "This answer is taken directly from a sentence in the article text.",
                    "section": (sections[i] if sections and i < len(sections) else None),
                    "sort_order": i,
                }
            )

        # If we couldn't extract enough facts, create a couple of safe questions from sections
        if len(quiz) < 5:
            sec_list = [s for s in (sections or []) if isinstance(s, str) and s.strip()]
            if sec_list:
                for j, sec in enumerate(sec_list[: (5 - len(quiz))]):
                    quiz.append(
                        {
                            "question": f"Which of the following is a section listed in the article '{title}'?",
                            "options": [sec, "Overview", "Appendix", "Bibliography"],
                            "answer": sec,
                            "difficulty": "easy",
                            "explanation": "Section names are taken from the scraped article structure.",
                            "section": sec,
                            "sort_order": len(quiz),
                        }
                    )

        # Related topics: section names and frequent capitalized tokens
        caps = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b", text[:4000])
        cap_counts = Counter([c.strip() for c in caps if 3 <= len(c.strip()) <= 30])
        stop_topics = {
            "The",
            "A",
            "An",
            "And",
            "Or",
            "But",
            "However",
            "This",
            "That",
            "It",
            "In",
            "On",
            "By",
            "From",
            "As",
            "For",
            "With",
            "Without",
        }
        related = []
        related.extend([s for s in (sections or [])[:3] if isinstance(s, str)])
        related.extend([w for w, _ in cap_counts.most_common(10) if w not in stop_topics])
        related_topics = []
        for t in related:
            if t and t not in related_topics and t.lower() != title.lower():
                related_topics.append(t)
            if len(related_topics) >= 6:
                break

        return {
            "quiz": quiz[:10],
            "related_topics": related_topics,
            "key_entities": {"people": [], "organizations": [], "locations": []},
        }
    
    def _parse_llm_response(self, response: str, fallback_title: str) -> dict:
        """Parse LLM JSON response, with fallback handling."""
        # Try to extract JSON from response (in case of markdown code blocks)
        text = response.strip()
        
        # Remove markdown code blocks if present
        if "```json" in text:
            text = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            text = text.group(1).strip() if text else text
        elif "```" in text:
            text = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
            text = text.group(1).strip() if text else text
        
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    raise ValueError("Failed to parse LLM response as JSON")
            else:
                raise ValueError("No valid JSON found in LLM response")
        
        quiz = data.get("quiz", [])
        related_topics = data.get("related_topics", [])
        key_entities = data.get("key_entities")
        
        # Normalize key_entities
        if isinstance(key_entities, dict):
            key_entities = {
                "people": list(key_entities.get("people", []) or []),
                "organizations": list(key_entities.get("organizations", []) or []),
                "locations": list(key_entities.get("locations", []) or []),
            }
        else:
            key_entities = {"people": [], "organizations": [], "locations": []}
        
        # Validate and normalize quiz items
        validated_quiz = []
        for i, q in enumerate(quiz):
            if isinstance(q, dict) and "question" in q and "options" in q and "answer" in q:
                validated_quiz.append({
                    "question": str(q["question"]),
                    "options": list(q["options"])[:4] if isinstance(q["options"], list) else [],
                    "answer": str(q["answer"]),
                    "difficulty": str(q.get("difficulty", "medium")).lower(),
                    "explanation": str(q["explanation"]) if q.get("explanation") else None,
                    "section": str(q["section"]) if q.get("section") else None,
                    "sort_order": i,
                })
        
        return {
            "quiz": validated_quiz,
            "related_topics": [str(t) for t in related_topics] if isinstance(related_topics, list) else [],
            "key_entities": key_entities,
        }
