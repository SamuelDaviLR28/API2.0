from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import PatchFretePrazo

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/patch")
def post_patch(payload: dict, db: Session = Depends(get_db)):
    novo = Patch(dados=payload)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {"message": "Patch recebido", "id": novo.id}