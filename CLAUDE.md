# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Golden Book (练习册电子化app) is an exercise book digitization application that uses AI to parse exercise images, extract questions, and automatically grade student answers. The system consists of a FastAPI backend and a Vue 3 frontend.

## Development Commands

### Quick Start with Automation Scripts

**Deploy project (first time setup):**
```bash
./deploy.sh
```

**Start services:**
```bash
./start.sh
```

**Stop services:**
```bash
./stop.sh
```

**Package for deployment:**
```bash
./package.sh
```

See `DEPLOYMENT.md` for detailed deployment instructions.

### Backend (FastAPI + SQLAlchemy)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
venv/bin/uvicorn main:app --reload --port 8000
```

**Important**: Always use `venv/bin/uvicorn` (or activate the venv first) to ensure dependencies are loaded correctly. Requires Python 3.13+ with updated dependencies (SQLAlchemy 2.0.36+, greenlet 3.0+).

### Frontend (Vue 3 + Vite + TypeScript)
```bash
cd frontend
npm install
npm run dev          # Development server (port 5173)
npm run build        # Production build
npm run preview      # Preview production build
```

## Architecture

### Backend Structure

The backend follows a layered architecture:

- **main.py**: FastAPI application entry point with CORS middleware and router registration
- **database.py**: Async SQLAlchemy setup with SQLite (aiosqlite)
- **models.py**: SQLAlchemy ORM models defining the database schema
- **schemas.py**: Pydantic models for request/response validation
- **routers/**: API endpoint handlers organized by domain
  - `ai_config.py`: AI model configuration management
  - `uploads.py`: Image upload and AI parsing orchestration
  - `exams.py`: Exam and question CRUD operations
  - `sessions.py`: Practice session management and grading
- **services/**: Business logic layer
  - `ai_service.py`: Unified AI service supporting multiple providers (OpenAI, Anthropic/Claude, Qwen) via OpenAI-compatible API
  - `grader.py`: Answer grading logic for different question types

### Data Model Relationships

```
AIConfig (1) - stores AI provider configurations
Exam (1) --< (N) Question - exercises with multiple questions
Exam (1) --< (N) ExamSession - practice attempts
ExamSession (1) --< (N) SessionAnswer - student answers for each question
```

Key workflow:
1. Upload exercise images → AI parses questions → creates Exam with Questions
2. Upload answer image → AI extracts correct answers → updates Questions
3. Student starts practice → creates ExamSession
4. Student submits answers → creates SessionAnswers → grades and calculates score

### Frontend Structure

- **main.ts**: Vue app initialization with Element Plus UI library, Pinia state management, and custom math directive
- **router/index.ts**: Vue Router configuration with lazy-loaded views
- **api/index.ts**: Centralized API client using axios with typed interfaces
- **views/**: Page components
  - `ExamsView.vue`: Exam list and creation
  - `ExamDetailView.vue`: View/edit exam questions
  - `PracticeView.vue`: Student practice interface with real-time answer submission
  - `ResultsView.vue`: Graded results display
  - `SessionsView.vue`: Practice history
  - `SettingsView.vue`: AI configuration management
- **directives/math.ts**: Custom Vue directive for rendering LaTeX math expressions using KaTeX

### AI Service Architecture

The `ai_service.py` provides a unified interface for multiple AI providers:
- Supports OpenAI, Anthropic (Claude), Qwen, and custom OpenAI-compatible endpoints
- Handles provider-specific message format conversion (especially for Anthropic's multimodal API)
- Two main AI operations:
  - `parse_exercise_image()`: Extracts questions from exercise images
  - `parse_answer_image()`: Extracts correct answers from answer key images
- Uses structured JSON prompts to ensure consistent AI responses
- Includes JSON extraction logic to handle markdown code blocks in AI responses

### Grading System

The grading logic in `services/grader.py` handles different question types:
- **single/multi**: Exact match with correct_answer (case-insensitive, whitespace-trimmed)
- **fill**: Exact match for fill-in-the-blank questions
- **subjective**: Always awards full score (requires manual review)

## Key Technical Details

- Database: SQLite with async support (aiosqlite)
- File uploads stored in `backend/uploads/` directory
- CORS configured for localhost:5173 (Vite dev) and localhost:4173 (Vite preview)
- Frontend uses Element Plus for UI components
- Math expressions rendered with KaTeX via custom `v-math` directive
- API base URL: `/api` (proxied in development)

## Common Workflows

### Adding a new AI provider
1. Update `ai_service.py` to handle the provider's API format
2. Add provider detection logic in `_is_anthropic()` or create new helper
3. Implement client initialization and message conversion if needed
4. Test with `POST /api/ai-configs/{id}/test` endpoint

### Modifying question types
1. Update `question_type` enum in `models.py` and `schemas.py`
2. Add grading logic in `services/grader.py`
3. Update frontend question rendering in `PracticeView.vue`
4. Update AI parsing prompts in `ai_service.py` if needed

### Adding new exam metadata
1. Add column to `Exam` model in `models.py`
2. Update Pydantic schemas in `schemas.py`
3. Run the app to auto-create schema (SQLAlchemy creates tables on startup)
4. Update frontend TypeScript interfaces in `api/index.ts`
