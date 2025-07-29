from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import os
import json
from database import SessionLocal
from models.rastro import Rastro
from services.rastro_sender import enviar_rastro_para_toutbox

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/rastro")
async def receber_evento_rastro(
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

    events_data = payload.get("eventsData")
    if not events_data or not isinstance(events_data, list):
        raise HTTPException(status_code=400, detail="Payload deve conter 'eventsData' como lista.")

    for event in events_data:
        nfkey = event.get("nfKey")
        if not nfkey:
            continue

        # Garantir que 'files' esteja sempre como lista
        events = event.get("events") or [{}]
        first_event = events[0]
        files = first_event.get("files")
        if files is None:
            files = []

        rastro = Rastro(
            nfkey=nfkey,
            courier_id=event.get("CourierId"),
            event_code=first_event.get("eventCode"),
            description=first_event.get("description"),
            date=first_event.get("date"),
            address=first_event.get("address"),
            number=first_event.get("number"),
            city=first_event.get("city"),
            state=first_event.get("state"),
            receiver_document=first_event.get("receiverDocument"),
            receiver=first_event.get("receiver"),
            geo_lat=first_event.get("geo", {}).get("lat"),
            geo_long=first_event.get("geo", {}).get("long"),
            file_url=files[0].get("url") if files else None,
            file_description=files[0].get("description") if files else None,
            file_type=files[0].get("fileType") if files else None,
            status=None,
            response=None,
            enviado=False,
            payload=json.dumps({"eventsData": [event]})
        )
        db.add(rastro)

    db.commit()
    return {"message": "Eventos recebidos e salvos."}


@router.post("/rastro/enviar-pendentes")
async def enviar_todos_rastros_pendentes():
    db = SessionLocal()
    rastros = db.query(Rastro).filter(Rastro.enviado == False).all()

    resultados = []
    for rastro in rastros:
        # Usa o payload salvo, que já está no formato correto
        payload = json.loads(rastro.payload)
        resultado = await enviar_rastro_para_toutbox(payload, rastro.courier_id)

        rastro.status = resultado["status"]
        rastro.response = resultado["response"]
        rastro.enviado = resultado["status"] == "enviado"
        resultados.append({"nfkey": rastro.nfkey, "status": rastro.status})

    db.commit()
    db.close()

    return {"resultados": resultados}
