import httpx
import os
import json
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from database import get_db
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro
from models.pedido import Pedido
from security import verificar_api_key

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
TOUTBOX_API_URL = os.getenv("TOUTBOX_EVENT_API", "http://courier.toutbox.com.br/api/v1/Parcel/Event")
TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")

router = APIRouter()

def montar_payload_rastro(evento: dict, nfkey: str, courier_id: int):
    event = {
        "geo": evento.get("geo"),
        "city": evento.get("city"),
        "date": evento.get("date"),
        "files": evento.get("files", []),
        "state": evento.get("state"),
        "number": evento.get("number"),
        "address": evento.get("address"),
        "receiver": evento.get("receiver"),
        "eventCode": evento.get("eventCode"),
        "description": evento.get("description"),
        "receiverDocument": evento.get("receiverDocument")
    }
    return {
        "eventsData": [
            {
                "nfKey": nfkey,
                "events": [event],
                "CourierId": courier_id
            }
        ]
    }


async def enviar_rastro_para_toutbox(payload: dict):
    headers = {
        "Authorization": TOUTBOX_API_KEY,
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(TOUTBOX_API_URL, json=payload, headers=headers)

    status = "enviado" if response.status_code in (200, 204) else f"erro {response.status_code}"
    return {"status": status, "response": response.text}


async def enviar_rastros_pendentes(db: Session):
    pendentes = db.query(Rastro).filter(Rastro.status == "pendente").all()
    logger.info(f"Encontrados {len(pendentes)} rastros pendentes para envio.")

    for rastro in pendentes:
        try:
            logger.info(f"Processando NFKey: {rastro.nfkey}")

            pedido = db.query(Pedido).filter(Pedido.nfkey == rastro.nfkey).first()
            if not pedido:
                msg = "Pedido não encontrado"
                logger.error(f"{rastro.nfkey} - {msg}")
                rastro.status = "erro"
                rastro.response = msg
                db.commit()
                continue

            payload_dict = json.loads(rastro.payload)
            events_data = payload_dict.get("eventsData", [])

            if not events_data or not events_data[0].get("events"):
                msg = "Payload inválido ou sem eventos"
                logger.error(f"{rastro.nfkey} - {msg}")
                rastro.status = "erro"
                rastro.response = msg
                db.commit()
                continue

            courier_id = events_data[0].get("CourierId")
            if not courier_id:
                msg = "CourierId ausente no payload"
                logger.error(f"{rastro.nfkey} - {msg}")
                rastro.status = "erro"
                rastro.response = msg
                db.commit()
                continue

            evento = events_data[0]["events"][0]
            if not evento.get("eventCode"):
                msg = "Campo obrigatório 'eventCode' ausente no evento."
                logger.error(f"{rastro.nfkey} - {msg}")
                rastro.status = "erro"
                rastro.response = msg
                db.commit()
                continue

            payload_formatado = montar_payload_rastro(evento, rastro.nfkey, courier_id)
            resultado = await enviar_rastro_para_toutbox(payload_formatado)

            rastro.status = resultado["status"]
            rastro.response = resultado["response"]
            db.commit()

            historico = HistoricoRastro(
                nfkey=rastro.nfkey,
                payload=json.dumps(payload_formatado, ensure_ascii=False),
                status=rastro.status,
                response=resultado["response"]
            )
            db.add(historico)
            db.commit()

            logger.info(f"{rastro.nfkey} - Status: {rastro.status}")

        except Exception as e:
            erro_msg = f"Erro inesperado: {str(e)}"
            logger.exception(f"{rastro.nfkey} - {erro_msg}")
            rastro.status = "erro"
            rastro.response = erro_msg
            db.commit()


@router.post("/rastro", dependencies=[Depends(verificar_api_key)])
def receber_rastro(data: dict, db: Session = Depends(get_db)):
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

        for evento in eventos:
            if not evento.get("eventCode"):
                raise HTTPException(status_code=400, detail="Campo obrigatório 'eventCode' ausente no evento.")

        geo = eventos[0].get("geo") or {}

        rastro = Rastro(
            nfkey=nfkey,
            courier_id=courier_id,
            event_code=eventos[0].get("eventCode"),
            description=eventos[0].get("description"),
            date=eventos[0].get("date"),
            address=eventos[0].get("address"),
            number=eventos[0].get("number"),
            city=eventos[0].get("city"),
            state=eventos[0].get("state"),
            receiver_document=eventos[0].get("receiverDocument"),
            receiver=eventos[0].get("receiver"),
            geo_lat=geo.get("lat"),
            geo_long=geo.get("lng"),
            file_url=eventos[0].get("files")[0].get("url") if eventos[0].get("files") else None,
            file_description=eventos[0].get("files")[0].get("description") if eventos[0].get("files") else None,
            file_type=eventos[0].get("files")[0].get("type") if eventos[0].get("files") else None,
            status="pendente",
            response="",
            payload=json.dumps({"eventsData": [evento_data]}, ensure_ascii=False)
        )
        db.add(rastro)

    db.commit()
    return {"message": "Eventos recebidos com sucesso"}


@router.post("/enviar-pendentes", dependencies=[Depends(verificar_api_key)])
async def enviar_rastros(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(enviar_rastros_pendentes, db)
    return {"message": "Envio de rastros pendentes iniciado em background"}
