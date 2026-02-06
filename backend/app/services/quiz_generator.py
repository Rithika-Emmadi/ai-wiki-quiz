"""
Quiz generation using LangChain and Groq LLM.
Uses Groq free tier API (no credit card required).
"""
import json
import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..config import get_settings
from ..prompts.quiz_prompts import QUIZ_GENERATION_PROMPT


class QuizGenerator:
    """Generates quiz from Wikipedia article content using LLM."""
    
    def __init__(self):
        settings = get_settings()
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is required. Get a free API key (no card needed) from "
                "https://console.groq.com/keys"
            )
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
        prompt = ChatPromptTemplate.from_template(QUIZ_GENERATION_PROMPT)
        chain = prompt | self.llm | StrOutputParser()
        
        sections_str = ", ".join(sections) if sections else "Introduction"
        
        response = chain.invoke({
            "title": title,
            "sections": sections_str,
            "content": content,
        })
        
        return self._parse_llm_response(response, title)
    
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
