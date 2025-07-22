from fastapi import APIRouter, Header, HTTPException, Request, Body, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from database import SessionLocal
from models.patch import PatchUpdate
import httpx
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.patch("/patch")
async def enviar_patch_toutbox(
    payload: List[Dict[str, Any]] = Body(...),
    nfkey: str = "",
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(None)
):
    API_KEY = os.getenv("API_KEY")
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Chave de API inválida.")

    if not nfkey:
        raise HTTPException(status_code=400, detail="Parâmetro 'nfkey' é obrigatório.")

    url = f"http://production.toutbox.com.br/api/v1/External/Order?nfkey={nfkey}&courier_id=84"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=payload, timeout=10)
        status = "sucesso" if response.status_code < 300 else "erro"
        response_text = response.text
    except Exception as e:
        status = "erro"
        response_text = str(e)

    novo_patch = PatchUpdate(
        nfkey=nfkey,
        payload=payload,
        status=status,
        response=response_text
    )
    db.add(novo_patch)
    db.commit()

    return {
        "nfkey": nfkey,
        "status_envio": status,
        "resposta_toutbox": response_text
    }
