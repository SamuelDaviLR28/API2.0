from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any
from app.database import SessionLocal
from app.models import Cancelamento

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.put("/cancelar-suspender")
def cancelar_suspender(payload: Any, db: Session = Depends(get_db)):
    novo = Cancelamento(dados=payload)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {
        "message": "Cancelamento ou suspensão processado",
        "id": novo.id
    }