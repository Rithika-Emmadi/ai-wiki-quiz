"""
LangChain prompt templates for quiz and related-topic generation.
These prompts are designed to:
1. Ground outputs strictly in article content (minimize hallucination)
2. Generate diverse, factually correct questions
3. Vary difficulty levels appropriately
"""

# Main quiz generation prompt - designed to minimize hallucination by grounding in text
QUIZ_GENERATION_PROMPT = """You are an expert educational quiz creator. Your task is to generate a high-quality quiz based EXCLUSIVELY on the following Wikipedia article content.

CRITICAL RULES:
- Base ALL questions, options, answers, and explanations ONLY on information explicitly stated in the article text below.
- Do NOT add any information not present in the article. If unsure, omit the question.
- Each question must have exactly 4 options (A, B, C, D).
- Only ONE option should be correct. The correct answer must be explicitly supported by the article.
- Vary difficulty: include 2-3 easy, 2-4 medium, and 1-2 hard questions.
- Include 5-10 questions total.
- For explanations, cite the relevant section or fact from the article.

ARTICLE TITLE: {title}

ARTICLE SECTIONS: {sections}

ARTICLE CONTENT:
{content}

Generate the quiz as a valid JSON object with this exact structure (no markdown, no extra text):
{{
  "key_entities": {{
    "people": ["Person 1", "Person 2"],
    "organizations": ["Org 1", "Org 2"],
    "locations": ["Place 1", "Place 2"]
  }},
  "quiz": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Exact text of correct option",
      "difficulty": "easy|medium|hard",
      "explanation": "Brief explanation citing article content.",
      "section": "Section name this question relates to"
    }}
  ],
  "related_topics": ["Topic 1", "Topic 2", "Topic 3"]
}}

- "key_entities": Extract people, organizations, and locations explicitly mentioned in the article. Use empty arrays [] for any category with none.
- "related_topics": 3-6 Wikipedia topic names for further reading. Use names that work as Wikipedia article titles.
Output ONLY the JSON object, nothing else."""


# Related topics extraction prompt (optional - can be combined with main)
RELATED_TOPICS_PROMPT = """Based on the following Wikipedia article summary and sections, suggest 3-6 related Wikipedia topics that a reader might want to explore for further reading.

Article: {title}
Sections: {sections}

Return ONLY a JSON array of topic names (as they would appear in Wikipedia URLs), e.g.:
["Topic One", "Topic Two", "Topic Three"]
"""


# Key entities extraction prompt (for structured metadata)
KEY_ENTITIES_PROMPT = """Extract key entities from this Wikipedia article text. Return a JSON object with exactly these keys:
- people: list of person names mentioned
- organizations: list of organizations, institutions, companies
- locations: list of places, countries, cities

Article title: {title}

Content (first 3000 chars):
{content}

Return ONLY a valid JSON object with these three keys. Use empty arrays [] if none found.
"""
