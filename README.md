# HR Document Assistant — Production

A production-ready RAG (Retrieval-Augmented Generation) application for querying HR policy documents using OpenAI and ChromaDB.

## Architecture

```
┌─────────────────┐        HTTP        ┌─────────────────────┐
│   Streamlit UI  │  ◄──────────────►  │   FastAPI Backend   │
│   (frontend/)   │                    │   (backend/app/)    │
└─────────────────┘                    └────────┬────────────┘
                                                │
                                    ┌───────────┴───────────┐
                                    │   ChromaDB (db/)      │
                                    │   OpenAI API          │
                                    └───────────────────────┘
```

**Backend** — FastAPI REST API handling document ingestion, vector storage, and LLM-powered Q&A.

**Frontend** — Streamlit app for uploading PDFs and asking questions.

## Features

- PDF upload and ingestion with chunking
- MMR-based semantic retrieval via ChromaDB
- LLM-powered question answering with source citations
- API key authentication (optional — disabled in dev mode)
- Structured logging with configurable levels
- Centralized YAML configuration
- Docker + docker-compose for containerized deployment
- GitHub Actions CI/CD (lint, test, Docker build)
- Unit and integration tests with pytest

## Quick Start

### Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone and set up

```bash
git clone <repo-url> && cd HR_Document_Assistant_Production
```

### 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run
uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env if backend is not on localhost:8000

streamlit run app.py
```

App at http://localhost:8501

### 4. Docker (recommended)

```bash
# Copy env files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit backend/.env with your OPENAI_API_KEY
# Set BACKEND_URL=http://backend:8000 in frontend/.env

docker-compose up --build
```

## API Endpoints

| Method | Path      | Auth | Description                          |
|--------|-----------|------|--------------------------------------|
| GET    | `/health` | No   | Service health and vector store status |
| POST   | `/upload` | Yes  | Upload a PDF document                |
| POST   | `/ingest` | Yes  | Index an uploaded PDF into ChromaDB  |
| POST   | `/ask`    | Yes  | Ask a question about ingested docs   |

### Authentication

Set `APP_API_KEY` in your `.env` to enable API key auth.  Pass the key via the `X-API-Key` header.  If `APP_API_KEY` is not set, auth is disabled (dev mode).

## Configuration

All settings are in `config/config.yaml`:

- **llm** — model name, temperature
- **embeddings** — model name
- **chunking** — chunk size, overlap
- **retriever** — search type, k
- **vector_store** — persist directory
- **upload** — allowed extensions, max file size, upload directory
- **logging** — level, format
- **server** — host, port

Override the config file path via `CONFIG_PATH` environment variable.

## Testing

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── auth.py            # API key authentication
│   │   ├── config.py          # YAML config loader
│   │   ├── logging_config.py  # Structured logging
│   │   ├── models.py          # Pydantic models
│   │   ├── document_loaders.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── llm.py
│   │   ├── vectorstore.py
│   │   ├── rag_pipeline.py
│   │   └── prompts.py
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── app.py                 # Streamlit app
│   ├── Dockerfile
│   └── requirements.txt
├── config/
│   └── config.yaml
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## License

MIT
