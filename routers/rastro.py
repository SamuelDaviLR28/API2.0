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
    API_KEY = os.getenv("API_KEY")
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Chave de API inválida.")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido.")

    event = payload.get("eventsData", [{}])[0]
    nfkey = event.get("nfKey")
    if not nfkey:
        raise HTTPException(status_code=400, detail="nfKey não encontrada.")

    TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")
    if not TOUTBOX_API_KEY:
        raise HTTPException(status_code=500, detail="Token Toutbox não configurado.")

    toutbox_payload = {
        "nfKey": event.get("nfKey"),
        "CourierId": event.get("CourierId"),
        "events": [{
            "eventCode": event.get("eventCode"),
            "description": event.get("description"),
            "date": event.get("date"),
            "address": event.get("address"),
            "number": event.get("number"),
            "city": event.get("city"),
            "state": event.get("state"),
            "receiverDocument": event.get("receiverDocument"),
            "receiver": event.get("receiver"),
            "geo": event.get("geo"),
            "files": event.get("files")
        }]
    }

    headers = {
        "Authorization": f"Bearer {TOUTBOX_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://courier.toutbox.com.br/api/v1/Parcel/Event",
                json=toutbox_payload,
                headers=headers,
                timeout=10
            )
        status_envio = "sucesso" if response.status_code < 300 else f"erro {response.status_code}"
        resposta = response.text
    except Exception as e:
        status_envio = "erro"
        resposta = str(e)

    rastro = Rastro(
        nfkey=nfkey,
        courier_id=event.get("CourierId"),
        event_code=event.get("eventCode"),
        description=event.get("description"),
        date=event.get("date"),
        address=event.get("address"),
        number=event.get("number"),
        city=event.get("city"),
        state=event.get("state"),
        receiver_document=event.get("receiverDocument"),
        receiver=event.get("receiver"),
        geo_lat=event.get("geo", {}).get("lat"),
        geo_long=event.get("geo", {}).get("long"),
        file_url=(event.get("files") or [{}])[0].get("url"),
        file_description=(event.get("files") or [{}])[0].get("description"),
        file_type=(event.get("files") or [{}])[0].get("fileType"),
        status=status_envio,
        response=resposta,
        enviado=(status_envio == "sucesso"),
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
