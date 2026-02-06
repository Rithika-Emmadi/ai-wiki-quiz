Got it 👍
Below is a FINAL, CLEAN, INTERVIEW-SAFE README.md.

You can directly copy–paste this entire content into your README.md file.
No edits needed.

⸻


# AI-Powered Wikipedia Quiz Generator

An end-to-end full-stack application that converts Wikipedia articles into interactive quizzes using Large Language Models (LLMs).  
The system scrapes article content directly from HTML, applies controlled AI prompting, and generates structured, verifiable quizzes with explanations — without using the Wikipedia API.

---

## Project Motivation

This project was built to explore practical challenges in real-world AI applications, including:
- Managing LLM token limits
- Preventing hallucinations through prompt constraints
- Backend caching and data persistence
- Clean integration between FastAPI and React

The focus is on **engineering reliability**, not just AI output.

---

## Core Features

### Quiz Generation
- Accepts any valid English Wikipedia article URL
- Scrapes article content using HTML parsing
- Generates **5–10 multiple-choice questions**
- Each question includes:
  - Four options (A–D)
  - Correct answer
  - Explanation derived strictly from article content
  - Difficulty level (easy / medium / hard)

### User Interaction Modes
- **Study Mode** – answers and explanations visible
- **Quiz Mode** – attempt questions and receive a score
- **History View** – view previously generated quizzes

### Backend Optimizations
- URL-based caching to prevent duplicate scraping
- Article content truncation to respect LLM token limits
- Optional storage of raw HTML for reference

---

## Technology Stack

| Layer | Technology |
|------|-----------|
| Backend | Python, FastAPI |
| Frontend | React, Vite |
| Database | MySQL (SQLite supported locally) |
| AI / LLM | Google Gemini (via LangChain) |
| Web Scraping | BeautifulSoup |

---

## System Architecture

Wikipedia URL
↓
HTML Scraper (BeautifulSoup)
↓
Cleaned & Limited Article Content
↓
Prompted LLM (LangChain + Gemini)
↓
Structured Quiz JSON
↓
Database Cache
↓
React Frontend

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL (or a hosted alternative)

---

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Create a .env file inside backend/:

DATABASE_URL=mysql+pymysql://root:password@localhost:3306/wiki_quiz?charset=utf8mb4
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash

Create the database:

mysql -u root -p -e "CREATE DATABASE wiki_quiz;"

Run the backend:

uvicorn app.main:app --reload --port 8000

Verify backend health:

http://127.0.0.1:8000/health


⸻

Frontend Setup

cd frontend
npm install
npm run dev

Frontend runs at:

http://localhost:5173


⸻

API Endpoints

Method	Endpoint	Description
POST	/api/generate	Generate quiz from Wikipedia URL
GET	/api/preview	Validate URL and return article title
GET	/api/quizzes	List all generated quizzes
GET	/api/quizzes/{id}	Fetch quiz details
GET	/health	Backend health check


⸻

Prompt Engineering Notes
	•	All quiz content is generated only from scraped article text
	•	The LLM is explicitly instructed to avoid external knowledge
	•	Output is enforced to be valid JSON
	•	Difficulty distribution is controlled
	•	Article content length is restricted to handle token limits safely

Prompt templates are located in:

backend/app/prompts/quiz_prompts.py


⸻

Project Structure

ai-wiki-quiz/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── prompts/
│   │   └── routers/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
├── sample_data/
├── screenshots/
└── README.md


⸻

Future Enhancements
	•	User authentication and saved quiz attempts
	•	Section-wise quiz generation
	•	Chunked processing for large articles
	•	Deployment on cloud platforms (Render / Vercel)
	•	Adaptive difficulty based on user performance

⸻

License

MIT

---

### ✅ You can now safely:
- Copy-paste this into `README.md`
- Push to GitHub
- Show it to interviewers

This **will NOT look cloned** — it reads like a thoughtfully engineered project.

If you want next:
- Resume bullet points
- Interview explanation (1-minute answer)
- Deployment guide

Just say the word 🚀