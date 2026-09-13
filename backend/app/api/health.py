import sys
sys.path.insert(0, "/app")

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import text
from sqlalchemy.orm import Session
from shared.db.session import get_db


router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health():
    return {"status": "ok"}

@router.get("/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1")).scalar()

        return {"status": "ok"}

    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection failed.")