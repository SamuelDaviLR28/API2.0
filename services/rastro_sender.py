import json
import logging
import asyncio
import httpx
from datetime import datetime, timezone
import os
from sqlalchemy.orm import Session
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro
from models.patch import PatchUpdate
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TOUTBOX_API_URL_RASTRO = "http://courier.toutbox.com.br/api/v1/Parcel/Event"
TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")
MAX_TENTATIVAS = 5

async def enviar_rastro_para_toutbox(payload: dict):
    headers = {
        "Authentication": TOUTBOX_API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(TOUTBOX_API_URL_RASTRO, json=payload, headers=headers)

    if response.status_code in (200, 204):
        status = "enviado"
    else:
        status = f"erro {response.status_code}"
    return {"status": status, "response": response.text}

async def enviar_rastros_pendentes(db: Session):
    rastros = db.query(Rastro).join(
        PatchUpdate,
        (Rastro.nfkey == PatchUpdate.nfkey) & (Rastro.courier_id == PatchUpdate.courier_id)
    ).filter(
        ((Rastro.status == "pendente") | (Rastro.status.startswith("erro"))) &
        (Rastro.tentativas_envio < MAX_TENTATIVAS) &
        (Rastro.em_processo == False) &
        (PatchUpdate.status.in_([200, 204]))
    ).all()

    logger.info(f"Enviando {len(rastros)} rastros pendentes com patch confirmado...")

    for rastro in rastros:
        try:
            rastro.em_processo = True
            rastro.tentativas_envio += 1
            db.commit()

            payload_dict = json.loads(rastro.payload)
            events_data = payload_dict.get("eventsData", [])

            if not events_data:
                raise ValueError("Payload sem eventsData")

            courier_id = events_data[0].get("CourierId")
            eventos = events_data[0].get("events", [])

            # Verifica se todos os eventos têm eventCode válido
            for evento in eventos:
                event_code = evento.get("eventCode")
                if not event_code or not event_code.strip():
                    raise ValueError(f"Evento com eventCode inválido em nfkey {rastro.nfkey}")

            payload_corrigido = {
                "eventsData": [
                    {
                        "nfKey": rastro.nfkey,
                        "events": eventos,
                        "CourierId": courier_id,
                    }
                ]
            }

            resultado = await enviar_rastro_para_toutbox(payload_corrigido)

            rastro.status = resultado["status"]
            rastro.response = resultado["response"]
            rastro.enviado = resultado["status"] == "enviado"
            rastro.em_processo = False
            db.commit()

            historico = HistoricoRastro(
                nfkey=rastro.nfkey,
                payload=json.dumps(payload_corrigido, ensure_ascii=False),
                status=rastro.status,
                response=resultado["response"]
            )
            db.add(historico)
            db.commit()

            await asyncio.sleep(0.5)

        except Exception as e:
            logger.exception(f"Erro ao enviar rastro NFKey {rastro.nfkey}: {e}")
            rastro.status = "erro"
            rastro.response = str(e)
            rastro.em_processo = False
            db.commit()
