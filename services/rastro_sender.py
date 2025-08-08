import httpx
import os
import json
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro
from models.pedido import Pedido

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
TOUTBOX_API_URL = os.getenv("TOUTBOX_EVENT_API", "http://courier.toutbox.com.br/api/v1/Parcel/Event")
TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")


def montar_payload_rastro(evento: dict, nfkey: str, courier_id: int):
    """Monta o payload no formato esperado pelo TOUTBOX"""
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


async def enviar_rastro_para_toutbox(payload: dict, courier_id: int):
    """Envia o payload formatado para a API do TOUTBOX"""
    headers = {
        "Authorization": TOUTBOX_API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(TOUTBOX_API_URL, json=payload, headers=headers)

    status = "enviado" if response.status_code in (200, 204) else f"erro {response.status_code}"
    return {"status": status, "response": response.text}


async def enviar_rastros_pendentes(db: Session):
    """Envia todos os rastros com status 'pendente' para o TOUTBOX"""
    pendentes = db.query(Rastro).filter(Rastro.status == "pendente").all()
    logger.info(f"Encontrados {len(pendentes)} rastros pendentes para envio.")

    for rastro in pendentes:
        try:
            logger.info(f"Processando NFKey: {rastro.nfkey}")

            # Busca pedido vinculado
            pedido = db.query(Pedido).filter(Pedido.nfkey == rastro.nfkey).first()
            if not pedido:
                msg = "Pedido não encontrado"
                logger.error(f"{rastro.nfkey} - {msg}")
                rastro.status = "erro"
                rastro.response = msg
                db.commit()
                continue

            # Carrega e valida payload original
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

            # Monta payload no formato exigido pelo TOUTBOX
            evento = events_data[0]["events"][0]
            payload_formatado = montar_payload_rastro(evento, rastro.nfkey, courier_id)

            # Envia para o TOUTBOX
            resultado = await enviar_rastro_para_toutbox(payload_formatado, courier_id)

            # Atualiza status no banco
            rastro.status = resultado["status"]
            rastro.response = resultado["response"]
            db.commit()

            # Salva histórico
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

