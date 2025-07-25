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

@router.patch("/")
async def enviar_patch(
    payload: List[Dict[str, Any]] = Body(...),
    nfkey: str = "",
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    # A autenticação já ocorre no middleware do main.py, mas pode repetir se quiser
    if not nfkey:
        raise HTTPException(status_code=400, detail="Parâmetro 'nfkey' é obrigatório.")

    # Exemplo simplificado: salvar patch no banco
    novo_patch = PatchUpdate(nfkey=nfkey, payload=payload, status="pendente")
    db.add(novo_patch)
    db.commit()
    db.refresh(novo_patch)

    return {"message": "Patch salvo e será enviado.", "id": novo_patch.id}
