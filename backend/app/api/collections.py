import sys
import os
sys.path.insert(0, "/app")

from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_user
from shared.db.session import get_db
from shared.models.user import User
from shared.models.collection import Collection
from shared.models.document import Document
from shared.models.chunk import Chunk


class CollectionCreate(BaseModel):
    name: str

class CollectionResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


router = APIRouter(prefix="/collections", tags=["collections"])


@router.post("/", response_model=CollectionResponse)
def create_collection(payload: CollectionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    collection = Collection(
        user_id=current_user.id,
        name=payload.name,
    )

    db.add(collection)
    db.commit()
    db.refresh(collection)

    return collection


@router.get("/", response_model=List[CollectionResponse])
def get_collections(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Collection).filter(Collection.user_id == current_user.id)

    return query.order_by(Collection.created_at.desc()).all()


@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection_by_id(collection_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id,
    ).first()

    if collection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    return collection


@router.delete("/{collection_id}")
def delete_collection(collection_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id,
    ).first()

    if collection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")


    documents = db.query(Document).filter(Document.collection_id == collection.id).all()

    for document in documents:
        db.query(Chunk).filter(Chunk.document_id == document.id).delete()

        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        db.delete(document)

    db.delete(collection)
    db.commit()

    return { "status": "deleted" }