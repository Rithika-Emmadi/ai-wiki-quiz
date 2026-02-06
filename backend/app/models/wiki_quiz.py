"""Database models for Wiki Quiz storage."""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class WikiQuiz(Base):
    """Main table storing Wikipedia quiz metadata and extracted content."""
    
    __tablename__ = "wiki_quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(512), unique=True, nullable=False, index=True)
    title = Column(String(256), nullable=False)
    summary = Column(Text, nullable=True)
    raw_html = Column(Text, nullable=True)  # Bonus: store raw HTML for reference
    key_entities = Column(JSON, nullable=True)  # {"people": [], "organizations": [], "locations": []}
    sections = Column(JSON, nullable=True)  # ["Early life", "World War II", ...]
    related_topics = Column(JSON, nullable=True)  # ["Cryptography", "Enigma machine", ...]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to quiz questions
    questions = relationship("QuizQuestion", back_populates="wiki_quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    """Individual quiz question with options and answer."""
    
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    wiki_quiz_id = Column(Integer, ForeignKey("wiki_quizzes.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # ["A", "B", "C", "D"]
    answer = Column(String(512), nullable=False)
    difficulty = Column(String(32), nullable=False)  # easy, medium, hard
    explanation = Column(Text, nullable=True)
    section = Column(String(256), nullable=True)  # For section-wise grouping (bonus)
    sort_order = Column(Integer, default=0)
    
    wiki_quiz = relationship("WikiQuiz", back_populates="questions")
