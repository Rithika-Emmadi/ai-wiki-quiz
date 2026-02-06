"""
API endpoints for quiz generation and history.
"""
import logging
import requests

logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import WikiQuiz, QuizQuestion
from ..schemas import WikiQuizResponse, WikiQuizListResponse, GenerateQuizRequest
from ..services import WikipediaScraper, QuizGenerator

router = APIRouter(prefix="/api", tags=["quiz"])


@router.get("/preview")
def preview_url(url: str):
    """
    Validate Wikipedia URL and return article title (bonus: URL validation and preview).
    Query param: url
    """
    scraper = WikipediaScraper()
    if not scraper.is_valid_wikipedia_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid Wikipedia URL. Use format: https://en.wikipedia.org/wiki/Article_Name",
        )
    try:
        title = scraper.fetch_title_only(url)
        return {"valid": True, "title": title, "url": url}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_quiz_generator():
    """Dependency for QuizGenerator (lazy init to avoid import-time API key check)."""
    try:
        return QuizGenerator()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=WikiQuizResponse)
def generate_quiz(
    request: GenerateQuizRequest,
    db: Session = Depends(get_db),
    generator: QuizGenerator = Depends(get_quiz_generator),
):
    """
    Generate a quiz from a Wikipedia article URL.
    Scrapes the page, sends to LLM, stores in DB, returns JSON.
    """
    scraper = WikipediaScraper()
    
    # URL validation
    if not scraper.is_valid_wikipedia_url(request.url):
        raise HTTPException(
            status_code=400,
            detail="Invalid Wikipedia URL. Use format: https://en.wikipedia.org/wiki/Article_Name"
        )
    
    # Check cache: avoid duplicate scraping (bonus)
    existing = db.query(WikiQuiz).filter(WikiQuiz.url == request.url).first()
    if existing:
        return _wiki_quiz_to_response(existing)
    
    # Scrape
    try:
        scraped = scraper.fetch_and_parse(request.url)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Generate quiz with LLM
    try:
        generated = generator.generate_quiz(
            title=scraped["title"],
            sections=scraped.get("sections", []),
            content=scraped["content"],
        )
    except Exception as e:
        logger.exception("Quiz generation failed")
        err_msg = str(e)
        if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
            raise HTTPException(
                status_code=429,
                detail="Gemini API quota exceeded. Wait for reset (midnight Pacific) or use a new API key.",
            )
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {err_msg}")
    
    # Store in database (key_entities from LLM; fallback to scraped if available)
    wiki_quiz = WikiQuiz(
        url=request.url,
        title=scraped["title"],
        summary=scraped.get("summary"),
        raw_html=scraped.get("raw_html"),
        key_entities=generated.get("key_entities") or scraped.get("key_entities"),
        sections=scraped.get("sections"),
        related_topics=generated.get("related_topics", []),
    )
    db.add(wiki_quiz)
    db.flush()  # Get wiki_quiz.id
    
    for q in generated.get("quiz", []):
        question = QuizQuestion(
            wiki_quiz_id=wiki_quiz.id,
            question=q["question"],
            options=q["options"],
            answer=q["answer"],
            difficulty=q.get("difficulty", "medium"),
            explanation=q.get("explanation"),
            section=q.get("section"),
            sort_order=q.get("sort_order", 0),
        )
        db.add(question)
    
    db.commit()
    db.refresh(wiki_quiz)
    
    return _wiki_quiz_to_response(wiki_quiz)


@router.get("/quizzes", response_model=list[WikiQuizListResponse])
def list_quizzes(db: Session = Depends(get_db)):
    """List all past quizzes (history)."""
    results = (
        db.query(WikiQuiz.id, WikiQuiz.url, WikiQuiz.title, WikiQuiz.created_at)
        .order_by(WikiQuiz.created_at.desc())
        .all()
    )
    
    # Get question counts
    counts = (
        db.query(QuizQuestion.wiki_quiz_id, func.count(QuizQuestion.id))
        .group_by(QuizQuestion.wiki_quiz_id)
        .all()
    )
    count_map = {wid: c for wid, c in counts}
    
    return [
        WikiQuizListResponse(
            id=r.id,
            url=r.url,
            title=r.title,
            created_at=r.created_at,
            question_count=count_map.get(r.id, 0),
        )
        for r in results
    ]


@router.get("/quizzes/{quiz_id}", response_model=WikiQuizResponse)
def get_quiz_details(quiz_id: int, db: Session = Depends(get_db)):
    """Get full quiz details by ID (for Details modal)."""
    wiki_quiz = db.query(WikiQuiz).filter(WikiQuiz.id == quiz_id).first()
    if not wiki_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return _wiki_quiz_to_response(wiki_quiz)


def _wiki_quiz_to_response(wiki_quiz: WikiQuiz) -> WikiQuizResponse:
    """Convert WikiQuiz model to response schema."""
    questions = sorted(wiki_quiz.questions, key=lambda q: q.sort_order)
    return WikiQuizResponse(
        id=wiki_quiz.id,
        url=wiki_quiz.url,
        title=wiki_quiz.title,
        summary=wiki_quiz.summary,
        key_entities=wiki_quiz.key_entities,
        sections=wiki_quiz.sections,
        related_topics=wiki_quiz.related_topics or [],
        quiz=[
            {
                "id": q.id,
                "question": q.question,
                "options": q.options,
                "answer": q.answer,
                "difficulty": q.difficulty,
                "explanation": q.explanation,
                "section": q.section,
                "sort_order": q.sort_order,
            }
            for q in questions
        ],
        created_at=wiki_quiz.created_at,
    )
