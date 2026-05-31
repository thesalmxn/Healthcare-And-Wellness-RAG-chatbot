# Health & Wellness LLM Chatbot

A bilingual Greek-English health and wellness chatbot that uses retrieval-augmented generation (RAG) to answer health-related questions from PDF documents.

## Features

- Greek and English bilingual support
- Document retrieval using FAISS
- Vectorized search over local healthcare content
- Modular pipeline for ingestion, retrieval, and chat

## Requirements

- Python 3.11+
- Installed Python dependencies from `requirements.txt`
- Optional: Ollama or another local LLM backend if configured

## Installation

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Usage

- `main.py` or `app.py` can be used to start the chatbot application.
- `src/ingest/build_index.py` builds or updates the FAISS index from PDF content.
- `src/retrieval/retriever.py` handles vector search and query retrieval.
- `src/chat/chat.py` contains the chat interface logic.

## Project Structure

- `data/` – source and raw PDF assets
- `vector_store/` – serialized FAISS index files
- `src/` – application source code
- `requirements.txt` – Python dependencies

## Notes

- Keep generated files and local environment files out of version control.
- If you use a local `.env` or model API keys, do not commit them.
