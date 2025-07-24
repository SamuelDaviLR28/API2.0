from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database import SessionLocal
from models.rastro import Rastro
import httpx
import os

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
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(None)
):
    API_KEY = os.getenv("API_KEY")
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Chave de API inválida.")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido.")

    try:
        nfkey = payload["eventsData"][0]["nfKey"]
    except Exception:
        raise HTTPException(status_code=400, detail="nfKey não encontrado no corpo.")

    url = "http://production.toutbox.com.br/api/v1/External/Tracking"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
        status = "sucesso" if response.status_code < 300 else "erro"
        resposta = response.text
    except Exception as e:
        status = "erro"
        resposta = str(e)

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


# Alias da rota para ESL
@router.post("/docs/api/esl/eventos")
async def receber_evento_esl_alias(
    request: Request,
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(None)
):
    return await enviar_rastro_toutbox(request, db, x_api_key)
