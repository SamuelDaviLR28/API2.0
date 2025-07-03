from fastapi import APIRouter, Request, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import SessionLocal
from models.rastro import Rastro

import httpx

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/rastro")
async def enviar_rastro_toutbox(
    request: Request,
    x_api_key: Optional[str] = Header(None)
):
    db: Session = next(get_db())

    # Lê o corpo da requisição
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido.")

    # Extrai nfKey (do primeiro evento)
    try:
        nfkey = payload["eventsData"][0]["nfKey"]
    except Exception:
        raise HTTPException(status_code=400, detail="nfKey não encontrado no corpo.")

    # URL da Toutbox
    url = "http://production.toutbox.com.br/api/v1/external/api/v1/External/Tracking"

    # Envia request
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
        status = "sucesso" if response.status_code < 300 else "erro"
        resposta = response.text
    except Exception as e:
        status = "erro"
        resposta = str(e)

    # Salva no banco
    rastro = Rastro(
        nfkey=nfkey,
        payload=payload,
        status=status,
        response=resposta
    )
    db.add(rastro)
    db.commit()

    return {
        "nfkey": nfkey,
        "status_envio": status,
        "resposta_toutbox": resposta
    }
