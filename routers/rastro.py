from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from models.rastro import Rastro
from services.rastro_sender import enviar_rastros_pendentes
from security import verificar_api_key
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/rastro", dependencies=[Depends(verificar_api_key)])
def receber_rastro(data: dict, db: Session = Depends(get_db)):
    try:
        events_data = data.get("eventsData", [])
        if not events_data:
            raise HTTPException(status_code=400, detail="Payload sem 'eventsData'")

        for evento_data in events_data:
            nfkey = evento_data.get("nfKey")
            courier_id = evento_data.get("CourierId")
            eventos = evento_data.get("events", [])

            if not nfkey or courier_id is None:
                raise HTTPException(status_code=400, detail="Campos obrigatórios faltando: 'nfKey' ou 'CourierId'")

            if not eventos:
                raise HTTPException(status_code=400, detail="Nenhum evento informado")

            evento = eventos[0]
            geo = evento.get("geo") or {}

            rastro = Rastro(
                nfkey=nfkey,
                courier_id=courier_id,
                event_code=evento.get("eventCode"),
                description=evento.get("description"),
                date=evento.get("date"),
                address=evento.get("address"),
                number=evento.get("number"),
                city=evento.get("city"),
                state=evento.get("state"),
                receiver_document=evento.get("receiverDocument"),
                receiver=evento.get("receiver"),
                geo_lat=geo.get("lat"),
                geo_long=geo.get("lng"),
                file_url=evento.get("files")[0].get("url") if evento.get("files") else None,
                file_description=evento.get("files")[0].get("description") if evento.get("files") else None,
                file_type=evento.get("files")[0].get("type") if evento.get("files") else None,
                status="pendente",
                response="",
                payload=json.dumps({"eventsData": [evento_data]}, ensure_ascii=False),
                tentativas_envio=0,
                em_processo=False,
                enviado=False,
            )
            db.add(rastro)

        db.commit()
        return {"message": "Eventos recebidos com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao receber rastro: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enviar-pendentes", dependencies=[Depends(verificar_api_key)])
async def enviar_rastros(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(enviar_rastros_pendentes, db)
    return {"message": "Envio de rastros pendentes iniciado em background"}
