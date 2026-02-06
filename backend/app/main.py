"""
AI Wiki Quiz Generator - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import quiz

app = FastAPI(
    title="AI Wiki Quiz Generator",
    description="Generate quizzes from Wikipedia articles using LLM",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quiz.router)


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()


@app.get("/")
def root():
    return {"message": "AI Wiki Quiz Generator API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
