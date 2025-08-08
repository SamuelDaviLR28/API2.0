import json
import logging
import asyncio
import httpx
import os
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TOUTBOX_API_URL = "http://courier.toutbox.com.br/api/v1/Parcel/Event"
TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")

MAX_TENTATIVAS = 5

def montar_payload_rastro(eventos_validos: list, nfkey: str, courier_id: int):
    """
    Monta o payload incluindo apenas eventos válidos.
    """
    return {
        "eventsData": [
            {
                "nfKey": nfkey,
                "events": eventos_validos,
                "CourierId": courier_id
            }
        ]
    }

async def enviar_rastro_para_toutbox(payload: dict):
    headers = {
        "Authorization": TOUTBOX_API_KEY,  # Atenção ao header correto
        "Content-Type": "application/json; charset=utf-8"
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(TOUTBOX_API_URL, json=payload, headers=headers)

    if response.status_code in (200, 204):
        status = "enviado"
    else:
        status = f"erro {response.status_code}"
    return {"status": status, "response": response.text}

async def enviar_rastros_pendentes(db: Session):
    pendentes = db.query(Rastro).filter(
        ((Rastro.status == "pendente") | (Rastro.status == "erro")) &
        (Rastro.tentativas_envio < MAX_TENTATIVAS) &
        (Rastro.em_processo == False)
    ).all()

    logger.info(f"Encontrados {len(pendentes)} rastros para enviar.")

    for rastro in pendentes:
        try:
            logger.info(f"Enviando rastro NFKey: {rastro.nfkey}")

            rastro.em_processo = True
            rastro.tentativas_envio += 1
            db.commit()

            payload_dict = json.loads(rastro.payload)
            events_data = payload_dict.get("eventsData", [])

            if not events_data:
                raise ValueError("Payload sem eventsData")

            courier_id = events_data[0].get("CourierId")
            if not courier_id:
                raise ValueError("CourierId ausente no payload")

            eventos = events_data[0].get("events", [])
            if not eventos:
                raise ValueError("Nenhum evento no payload")

            # Filtrar apenas eventos que tenham eventCode válido
            eventos_validos = []
            for evento in eventos:
                if evento.get("eventCode") and isinstance(evento.get("eventCode"), (str, int)):
                    eventos_validos.append(evento)
                else:
                    logger.warning(f"Evento descartado por faltar eventCode válido: {evento}")

            if not eventos_validos:
                # Se não houver evento válido, marca como erro e continua
                rastro.status = "erro"
                rastro.response = "Nenhum evento com eventCode válido para envio."
                rastro.em_processo = False
                db.commit()
                logger.error(f"Rastro NFKey {rastro.nfkey} não possui eventos válidos para envio.")
                continue

            # Monta o payload só com eventos válidos
            payload_formatado = montar_payload_rastro(eventos_validos, rastro.nfkey, courier_id)
            resultado = await enviar_rastro_para_toutbox(payload_formatado)

            rastro.status = resultado["status"]
            rastro.response = resultado["response"]

            if resultado["status"] == "enviado":
                rastro.enviado = True
                logger.info(f"Rastro NFKey {rastro.nfkey} enviado com sucesso.")
            else:
                logger.warning(f"Falha ao enviar rastro NFKey {rastro.nfkey}: {resultado['response']}")

            db.commit()

            historico = HistoricoRastro(
                nfkey=rastro.nfkey,
                payload=json.dumps(payload_formatado, ensure_ascii=False),
                status=rastro.status,
                response=resultado["response"]
            )
            db.add(historico)
            db.commit()

            rastro.em_processo = False
            db.commit()

            await asyncio.sleep(0.5)

        except Exception as e:
            logger.exception(f"Erro ao enviar rastro NFKey {rastro.nfkey}: {e}")
            rastro.status = "erro"
            rastro.response = str(e)
            rastro.em_processo = False
            db.commit()
