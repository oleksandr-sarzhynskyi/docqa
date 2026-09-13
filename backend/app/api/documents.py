import uuid
import os
import sys
sys.path.insert(0, "/app")

from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.security import get_current_user
from app.core.celery_client import app
from shared.db.session import get_db
from shared.models.user import User
from shared.models.collection import Collection
from shared.models.document import Document
from shared.models.chunk import Chunk


UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class DocumentResponse(BaseModel):
    id: int
    collection_id: int
    original_filename: str
    file_path: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    id: int
    original_filename: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


router = APIRouter(tags=["documents"])

def get_owned_collection(collection_id: int, current_user: User, db: Session) -> Collection:
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id
    ).first()

    if collection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    return collection

def get_owned_document(document_id: int, current_user: User, db: Session) -> Document:
    document = db.query(Document).join(Collection, Document.collection_id == Collection.id).filter(
        Document.id == document_id,
        Collection.user_id == current_user.id
    ).first()
    
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return document


@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    collection_id: int,
    file: UploadFile = File(description="File to upload"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    collection = get_owned_collection(collection_id, current_user, db)
    
    if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pdf files are allowed")
    
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / unique_filename

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    document = Document(
        collection_id = collection.id,
        original_filename = file.filename,
        file_path = str(file_path),
        status = "processing",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    app.send_task("tasks.process_document", args=[document.id])

    return document


@router.get("/collections/{collection_id}/documents", response_model=List[DocumentListResponse])
def list_documents(collection_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_owned_collection(collection_id, current_user, db)

    return db.query(Document).filter(Document.collection_id == collection_id).order_by(Document.created_at.desc()).all()


@router.get("/documents/{document_id}", response_model=DocumentListResponse)
def get_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = get_owned_document(document_id, current_user, db)

    return document


@router.get("/documents/{document_id}/file")
def get_document_file(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = get_owned_document(document_id, current_user, db)

    return FileResponse(document.file_path, media_type="application/pdf", filename=document.original_filename)


@router.delete("/documents/{document_id}")
def delete_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = get_owned_document(document_id, current_user, db)

    db.query(Chunk).filter(Chunk.document_id == document.id).delete()

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()

    return { "status": "deleted" }