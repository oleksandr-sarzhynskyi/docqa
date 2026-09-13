import sys
sys.path.insert(0, "/app")

from celery_app import app

from shared.db.session import SessionLocal

from shared.models.chunk import Chunk
from shared.models.document import Document
from shared.models.collection import Collection
from shared.models.user import User

from services.pdf_extractor import extract_text
from services.chunker import chunk_text
from services.embedder import create_embedding

@app.task
def process_document(document_id: int):
    db = SessionLocal()

    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if document is None:
            return

        pages = extract_text(document.file_path)
        chunks = chunk_text(pages)

        if not chunks:
            document.status = "failed"
            db.commit()
            return

        for chunk_index, chunk_data in enumerate(chunks):
            embedding = create_embedding(chunk_data["text"])

            db_chunk = Chunk(
                document_id = document.id,
                text = chunk_data["text"],
                embedding = embedding,
                chunk_index = chunk_index,
                page = chunk_data["page"],
            )

            db.add(db_chunk)

        document.status = "ready"

        db.commit()

    except Exception:
        db.rollback()
        if document:
            document.status = "failed"
            db.commit()
        raise

    finally:
        db.close()