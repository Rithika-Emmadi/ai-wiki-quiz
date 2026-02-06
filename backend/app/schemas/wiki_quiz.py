"""Pydantic schemas for API request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class QuizQuestionBase(BaseModel):
    question: str
    options: list[str]
    answer: str
    difficulty: str  # easy, medium, hard
    explanation: Optional[str] = None
    section: Optional[str] = None


class QuizQuestionCreate(QuizQuestionBase):
    sort_order: int = 0


class QuizQuestionResponse(QuizQuestionBase):
    id: int
    sort_order: int

    class Config:
        from_attributes = True


class KeyEntities(BaseModel):
    people: list[str] = []
    organizations: list[str] = []
    locations: list[str] = []


class WikiQuizBase(BaseModel):
    url: str
    title: str
    summary: Optional[str] = None
    key_entities: Optional[dict] = None
    sections: Optional[list[str]] = None
    related_topics: Optional[list[str]] = None


class WikiQuizCreate(WikiQuizBase):
    quiz: list[QuizQuestionCreate]
    raw_html: Optional[str] = None


class WikiQuizResponse(WikiQuizBase):
    id: int
    quiz: list[QuizQuestionResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class WikiQuizListResponse(BaseModel):
    id: int
    url: str
    title: str
    created_at: datetime
    question_count: int

    class Config:
        from_attributes = True


class GenerateQuizRequest(BaseModel):
    url: str  # Wikipedia URL
