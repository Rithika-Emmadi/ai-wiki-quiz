# AI Wiki Quiz Generator

Full-stack app that turns a Wikipedia URL into a quiz (Tab 1) and stores every generated quiz in a local database so **quiz history shows up in Tab 2** (with a details modal).

## Technology stack

- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: React + Vite
- **Database**: SQLite by default (`backend/wiki_quiz.db`)
- **LLM**: Groq via LangChain (optional). If no key is provided, the backend falls back to a local heuristic generator so the project still runs end-to-end.

## Run the project (Windows)

### Backend (FastAPI)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Health**: `http://127.0.0.1:8000/health`
- **Docs**: `http://127.0.0.1:8000/docs`

Optional Groq key (real LLM generation):

- Copy `backend/env.example` → `backend/.env` (create this file manually)
- Put your `GROQ_API_KEY=...` in it

### Frontend (React)

```powershell
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

Vite is configured to proxy `/api/*` → `http://127.0.0.1:8000` (see `frontend/vite.config.js`).

## API endpoints

- **POST** `/api/generate` — generate quiz from Wikipedia URL (and persist it)
- **GET** `/api/preview?url=...` — validate URL and fetch title
- **GET** `/api/quizzes` — list quiz history
- **GET** `/api/quizzes/{id}` — quiz details (used by the details modal)
- **GET** `/health` — health check

## Prompt templates (LangChain)

Prompt templates are in `backend/app/prompts/quiz_prompts.py`:

- `QUIZ_GENERATION_PROMPT`: quiz + related-topics generation (JSON-only output)
- `RELATED_TOPICS_PROMPT`: optional related topic-only prompt
- `KEY_ENTITIES_PROMPT`: optional entity extraction prompt

## Sample data

`sample_data/` contains:

- `urls_tested.txt`: URLs tested
- `*_quiz_output.json`: saved JSON outputs from calling `POST /api/generate`

## Screenshots

`screenshots/` contains:

- `tab1_generate_quiz.png`
- `tab2_history.png`
- `details_modal.png`

To regenerate screenshots (requires backend on `:8000` and frontend on `:5174`):

```powershell
cd frontend
npm install
npx playwright install chromium --with-deps

# start frontend on a dedicated port in a separate terminal:
# npx vite --host 127.0.0.1 --port 5174

$env:FRONTEND_URL="http://127.0.0.1:5174/"
npm run screenshots
```

## Repo note (duplicate folder)

There is also an `ai-wiki-quiz/` folder that mirrors the root project layout. The canonical runnable app is the **root** `backend/` and `frontend/`.