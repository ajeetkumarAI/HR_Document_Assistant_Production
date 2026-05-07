---
name: testing-hr-assistant
description: Test the HR Document Assistant Production app end-to-end. Use when verifying backend API, frontend UI, or auth changes.
---

# Testing HR Document Assistant Production

## Prerequisites

- Python 3.11+ with venv
- Backend dependencies: `cd backend && pip install -r requirements-dev.txt`
- Frontend dependencies: `cd frontend && pip install -r requirements.txt`

## Devin Secrets Needed

- `OPENAI_API_KEY` — Required for full RAG pipeline testing (document ingestion + QA). Without it, you can still test all API validation, auth, error handling, and frontend UI.

## Running Unit Tests

```bash
cd backend && source .venv/bin/activate && pytest tests/ -v --tb=short
```

Expected: 21 tests pass. These do NOT require an OpenAI key.

## Running Lint

```bash
cd backend && source .venv/bin/activate && ruff check app/ tests/ && ruff format --check app/ tests/
```

## Backend API Testing

1. Start the backend:
   ```bash
   cd backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. Test health endpoint:
   ```bash
   curl -s http://localhost:8000/health
   ```
   Expected: `{"status": "healthy", "version": "1.0.0", "vector_store_ready": false}`

3. Test upload validation (non-PDF rejected):
   ```bash
   curl -s -X POST http://localhost:8000/upload -F "file=@/dev/null;filename=test.txt"
   ```
   Expected: 400, detail contains "not allowed"

4. Test ask without documents:
   ```bash
   curl -s -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question":"test"}'
   ```
   Expected: 400, "No documents have been ingested"

5. Test empty question validation:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question":""}'
   ```
   Expected: 422

## Auth Testing

Restart backend with `APP_API_KEY=test-key`:
```bash
APP_API_KEY=test-key uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- Wrong key → 401: `curl -s -H "X-API-Key: wrong" -X POST http://localhost:8000/ask ...`
- Correct key → passes auth (400 for no vector store, NOT 401)
- No APP_API_KEY set → dev mode, auth disabled

## Frontend UI Testing

1. Start frontend (with backend already running):
   ```bash
   cd frontend && streamlit run app.py --server.headless true --server.port 8501
   ```

2. Open http://localhost:8501 in browser and verify:
   - Title: "HR Policy Assistant Chatbot"
   - Sidebar: "Backend: healthy" (green) and vector store status
   - Section 1: "Upload an HR Policy Document" with PDF uploader
   - Section 2: "Ask a Question" with text input and "Get Answer" button

3. Test empty question → yellow warning "Please enter a question."
4. Test question without documents → warning about no documents ingested

## Full RAG Pipeline Testing (requires OPENAI_API_KEY)

If `OPENAI_API_KEY` is available:
1. Set it in `backend/.env`
2. Upload a PDF via the frontend
3. Click "Upload & Ingest Document"
4. Ask a question about the document content
5. Verify answer with source citations

## Swagger Docs

FastAPI auto-docs available at http://localhost:8000/docs — shows all endpoints with request/response schemas.

## Tips

- The old Streamlit app from the original repo might be cached in the browser at localhost:8501. Use Ctrl+Shift+R to force-reload if you see the wrong UI.
- Backend logs are structured and printed to stdout — check the terminal for debugging.
- The `config/config.yaml` file controls all settings (LLM model, chunk size, retriever params, etc.).
