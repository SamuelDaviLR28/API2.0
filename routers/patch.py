from fastapi import APIRouter, Depends, Header, HTTPException, Body
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models.patch import PatchUpdate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
async def registrar_patch(
    nfkey: str,
    courier_id: int,
    db: Session = Depends(get_db)
):
    novo_patch = PatchUpdate(
        nfkey=nfkey,
        courier_id=courier_id,
        status=None  # Aguardando envio
    )
    db.add(novo_patch)
    db.commit()
    db.refresh(novo_patch)

    return {"message": "Patch registrado. Envio será feito automaticamente.", "id": novo_patch.id}

