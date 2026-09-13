# DocQA

**DocQA is a RAG application for asking questions about uploaded PDF documents.**

Documents are processed asynchronously, split into chunks, embedded with Gemini and stored in PostgreSQL database using pgvector. User questions are embedded and matched against document chunks before Gemini generates an answer based only on the retrieved context.

The project is designed around a separated API, background worker, database and frontend architecture.

This is a learning/portfolio project built with fake data, but designed and built the way real product would be.

## Architecture
```text
                    ┌──────────────┐
                    │    React     │
                    │   Frontend   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    │    Backend   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        PostgreSQL       Redis      Gemini API
        + pgvector                    │
              ▲                       │
              │                       │
              └────── Celery ─────────┘
                     Worker
```

## Document ingestion
```text
PDF Upload
    │
    ▼
FastAPI
    │
    ▼
Create Document
    │
    ▼
Celery Task
    │
    ├── Extract text
    ├── Split into chunks
    ├── Generate embeddings
    └── Store chunks + vectors
            │
            ▼
      PostgreSQL + pgvector
```

## Question answering
```text
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
Vector Similarity Search
      │
      ▼
Retrieve Relevant Chunks
      │
      ▼
Build Grounded Prompt
      │
      ▼
Gemini
      │
      ▼
Answer + Citations
```

## Features

- User registration and JWT authentication
- PDF documents upload
- Document collections
- Asynchronous document processing with Celery
- PDF text extraction
- Overlapping text chunking
- Gemini embeddings
- PostgreSQL vector storage with pgvector
- Semantic similarity search
- Retrieval-augmented generation (RAG)
- Answers based on retrieved document context
- Document citations
- Document processing status tracking
- Dockerized development environment
- PostgreSQL migrations with Alembic

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, pgvector, JWT authentication

**AI:** Google Gemini, Gemini embeddings

**Background processing:** Celery, Redis

**Frontend:** React, Vite

**Infrastructure:** Docker, Docker Compose

## RAG Pipeline

DocQA follows typical RAG pipeline.

**1. Ingestion**

User uploads PDF document. API stores document metadata and schedules background Celery task.

**2.Text extraction**

Worker extracts text from PDF using pdfplumber

**3. Chunking**

Extracted text is split into smaller overlapping chunks. They help preserve context when relevant information spans chunk boundaries.

**4. Embedding**

Each chunk is converted into a vector embedding using Gemini. Resulting vectors are stored in PostgreSQL using pgvector.

**5. Retrieval**

When user asks a question, it is embedded using the same model. Resulting vector is compared against stored document chunk vectors to retrieve the most relevant context.

**6. Generation**

Retrieved chunks are passed to Gemini as context. The model is instructed to answer using the retrieved document content rather than relying on unrelated information. If relevant information cannot be found in the context, application should indicate that answer was not found in the documents.

## Project Structure

```text
docqa/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   └── core/
│   ├── Dockerfile
│   └── requirements.txt
│
├── worker/
│   ├── services/
│   │   ├── pdf_extractor.py
│   │   ├── chunker.py
│   │   └── embedder.py
│   ├── celery_app.py
│   ├── tasks.py
│   └── Dockerfile
│
├── shared/
│   ├── db/
│   │   └── session.py
│   └── models/
│       ├── user.py
│       ├── collection.py
│       ├── document.py
│       └── chunk.py
│
├── frontend/
│   └── src/
│       ├── api/
│       ├── components/
│       └── pages/
│
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Data Model

```text
User
 │
 └── Collection
       │
       └── Document
             │
             └── Chunk
                    ├── text
                    ├── embedding
                    └── chunk_index
```


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`GEMINI_API_KEY`

`SECRET_KEY`

## Running it locally

**Requirements:** Docker and Docker Compose.

1. Copy the environment template and fill in your own values:

   ```
   cp .env.example .env
   ```
   You'll need a [Gemini API key](https://aistudio.google.com/apikey), and
   should generate a real random `SECRET_KEY` :

   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Start everything:

   ```
   docker compose up -d --build
   ```
3. Run the database migrations:

   ```
   docker compose exec backend alembic upgrade head
   ```
4. Open the app:

   - Frontend: [http://localhost:5173](http://localhost:5173)
   - Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Design decisions

**Why PostgreSQL + pgvector?**

Using PostgreSQL for relational data and vector search keeps the architecture relatively simple while still supporting semantic retrieval.

**Why Celery?**

PDF processing and embedding generation can be slow compared with normal API requests.

Moving ingestion into background worker prevents API request from blocking while document is being processed.

**Why shared/ package?**

Backend and Celery worker both need access to the database session and SQLAlchemy models.

This package eliminates the need to update models in multiple places.

## API Overview

| Method | Path     | Description |
| :-------- | :------- | :------- |
| `GET` | `/health` | Health |
| `GET` | `/health/db` | Database health |
|`POST`|`/auth/signup`| Sign up |
|`POST`|`/auth/login`| Login |
|`GET`|`/collections`| Get collections |
|`POST`|`/collections`| Create collection |
|`GET`|`/collections/{collection_id}`| Get collection by id |
|`DELETE`|`/collections/{collection_id}`| Delete collection |
|`POST`|`/documents/upload`| Upload document |
|`GET`|`/collections/{collection_id}/documents`| List of documents |
|`GET`|`/documents/{document_id}`|Get document |
|`DELETE`|`/documents/{document_id}`|Delete document |
|`GET`|`/documents/{document_id}/file`|Get document file |
|`POST`|`/collections/{collection_id}/query`|Query collection|