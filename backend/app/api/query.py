import sys
sys.path.insert(0, "/app")

from ..config import API_KEY, MODEL

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google import genai
from google.genai import types

from app.core.security import get_current_user
from shared.db.session import get_db
from shared.models.user import User
from shared.models.collection import Collection
from shared.models.chunk import Chunk
from shared.models.document import Document


client = genai.Client(api_key=API_KEY)


class QueryRequest(BaseModel):
    question: str

class Citation(BaseModel):
    document_id: int
    filename: str
    page: int
    chunk_index: int

class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]

class AnswerSchema(BaseModel):
    answer: str
    used_chunks: list[int]


def create_embedding(text: str):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768),
    )

    values = response.embeddings[0].values
    norm = sum(v * v for v in values) ** 0.5

    return [v / norm for v in values]


def generate_answer(question: str, results: list[tuple[Chunk, Document]]) -> AnswerSchema:
    context = "\n\n".join(
        f"[{i}] (from {document.original_filename}, page {chunk.page}):\n{chunk.text}"
        for i, (chunk, document) in enumerate(results, start=1)
    )

    prompt = f"""
    You are answering a question using ONLY the numbered context chunks below.

    Rules:
    - Base your answer strictly on the provided context. Do not use outside knowledge, even if you're confident it's correct.
    - If the context does not contain enough information to answer, say so explicitly rather than guessing.
    - Be direct and concise.
    - In "used_chunks", list only the chunk numbers you actually drew on to write the answer — omit chunks that were retrieved but not relevant.

    Context:
    {context}

    Question: {question}
    """

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AnswerSchema,
        ),
    )

    return AnswerSchema.model_validate_json(response.text)


router = APIRouter(tags=["query"])


@router.post("/collections/{collection_id}/query", response_model=QueryResponse)
def query_collection(
    collection_id: int,
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id,
    ).first()

    if collection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    question_embedding = create_embedding(request.question)

    results = (
        db.query(Chunk, Document)
        .join(Document, Chunk.document_id == Document.id)
        .filter(Document.collection_id == collection_id)
        .order_by(Chunk.embedding.cosine_distance(question_embedding))
        .limit(5)
        .all()
    )

    if not results:
        return QueryResponse(answer="No documents have been processed in this collection yet.", citations=[])

    parsed = generate_answer(request.question, results)

    citations = []
    for i in parsed.used_chunks:
        if 1 <= i <= len(results):
            chunk, document = results[i - 1]

            citations.append(Citation(
                document_id = document.id,
                filename = document.original_filename,
                page = chunk.page,
                chunk_index = chunk.chunk_index,
            ))

    return QueryResponse(answer=parsed.answer, citations=citations)