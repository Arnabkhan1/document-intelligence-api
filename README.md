
# Document Intelligence API

An evidence-grounded document intelligence platform
for document ingestion, semantic retrieval, and
AI-powered question answering.

## Features

- Document ingestion and parsing
- Structure-aware text chunking
- Semantic and keyword search
- Evidence-grounded question answering
- Document and page-level citations
- Secure, multi-tenant API

## Technology Stack

- Python 3.12+
- FastAPI
- Pydantic
- PostgreSQL
- pgvector
- PyMuPDF
- Pytest
- Docker

## Project Structure

Application code is maintained under `src/dia`.
Automated tests are maintained under `tests`.

## Local Development

### 1. Clone the repository

### 2. Create virtual environment

python -m venv .venv

### 3. Activate environment

Windows:

.venv\Scripts\activate

### 4. Install dependencies

pip install -e ".[dev]"

### 5. Start development server

uvicorn dia.main:app --reload --app-dir src

### 6. Run tests

python -m pytest -v

## API Documentation

Visit /docs when the development server is running.

## Development Status

Stage 1 - Engineering Foundation
