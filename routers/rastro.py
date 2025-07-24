from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database import SessionLocal
from models.rastro import Rastro
import httpx
import os
import json

from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

# Dependência do banco de dados
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
    # Autenticação via API Key
    API_KEY = os.getenv("API_KEY")
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Chave de API inválida.")

    # Validação do corpo JSON
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido.")

    # Extração da nfKey
    try:
        nfkey = payload["eventsData"][0]["nfKey"]
    except Exception:
        raise HTTPException(status_code=400, detail="nfKey não encontrada no corpo.")

    # URL e Token da Toutbox
    url = "https://production.toutbox.com.br/api/v1/External/Tracking"
    TBOX_TOKEN = os.getenv("TBOX_TOKEN")  # deve estar no seu .env

    # Headers com Authorization
    headers = {
        "Authorization": f"Bearer {TBOX_TOKEN}",
        "Content-Type": "application/json"
    }

    # Envio para a Toutbox
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10)
        status_envio = "sucesso" if response.status_code < 300 else "erro"
        resposta = response.text
    except Exception as e:
        status_envio = "erro"
        resposta = str(e)

    # Registro no banco
    rastro = Rastro(
        nfkey=nfkey,
        status=status_envio,
        response=resposta,
        enviado=(status_envio == "sucesso"),
        # payload é JSON na prática, então você precisa certificar que o campo no modelo está configurado para JSON (Text + cast no PostgreSQL ou JSON nativo)
        payload=json.dumps(payload)  
    )
    db.add(rastro)
    db.commit()

    return {
        "nfkey": nfkey,
        "status_envio": status_envio,
        "resposta_toutbox": resposta
    }

# Alias para ESL
@router.post("/docs/api/esl/eventos")
async def receber_evento_esl_alias(
    request: Request,
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(None)
):
    return await enviar_rastro_toutbox(request, db, x_api_key)
