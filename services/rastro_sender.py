import json
import logging
import asyncio
import httpx
from sqlalchemy.orm import Session
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro
from models.patch import PatchUpdate

logger = logging.getLogger(__name__)

TOUTBOX_API_URL_RASTRO = "http://courier.toutbox.com.br/api/v1/Parcel/Event"
MAX_TENTATIVAS = 5

async def enviar_rastro_para_toutbox(payload: dict, api_key: str):
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json; charset=utf-8"
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(TOUTBOX_API_URL_RASTRO, json=payload, headers=headers)

    if response.status_code in (200, 204):
        status = "enviado"
    else:
        status = f"erro {response.status_code}"
    return {"status": status, "response": response.text}

async def enviar_rastros_pendentes(db: Session, api_key: str):
    # Buscar rastros pendentes onde o patch correspondente está "enviado"
    rastros = db.query(Rastro).join(
        PatchUpdate,
        (Rastro.nfkey == PatchUpdate.nfkey) & (Rastro.courier_id == PatchUpdate.courier_id)
    ).filter(
        ((Rastro.status == "pendente") | (Rastro.status.like("erro%"))) &
        (Rastro.tentativas_envio < MAX_TENTATIVAS) &
        (Rastro.em_processo == False) &
        (PatchUpdate.status == "enviado")
    ).all()

    logger.info(f"Enviando {len(rastros)} rastros pendentes com patch confirmado...")

    for rastro in rastros:
        try:
            # Marcar que está em processo para evitar concorrência
            rastro.em_processo = True
            rastro.tentativas_envio = (rastro.tentativas_envio or 0) + 1
            db.add(rastro)
            db.commit()
            db.refresh(rastro)

            payload_dict = json.loads(rastro.payload)
            events_data = payload_dict.get("eventsData", [])

            if not events_data:
                raise ValueError("Payload sem eventsData")

            courier_id = events_data[0].get("CourierId")
            eventos = events_data[0].get("events", [])

            # Filtrar só eventos com eventCode válido (não vazio e não nulo)
            eventos_validos = [e for e in eventos if e.get("eventCode") and e.get("eventCode").strip()]
            if not eventos_validos:
                raise ValueError(f"Todos os eventos sem eventCode válido para nfkey {rastro.nfkey}")

            payload_corrigido = {
                "eventsData": [
                    {
                        "nfKey": rastro.nfkey,
                        "events": eventos_validos,
                        "CourierId": courier_id,
                    }
                ]
            }

            resultado = await enviar_rastro_para_toutbox(payload_corrigido, api_key)

            rastro.status = resultado["status"]
            rastro.response = resultado["response"][:255]
            rastro.enviado = resultado["status"] == "enviado"
            rastro.em_processo = False
            db.add(rastro)
            db.commit()
            db.refresh(rastro)

            historico = HistoricoRastro(
                nfkey=rastro.nfkey,
                payload=json.dumps(payload_corrigido, ensure_ascii=False),
                status=rastro.status,
                response=resultado["response"][:255]
            )
            db.add(historico)
            db.commit()

            await asyncio.sleep(0.5)

        except Exception as e:
            logger.exception(f"Erro ao enviar rastro NFKey {rastro.nfkey}: {e}")
            rastro.status = "erro"
            rastro.response = str(e)[:255]
            rastro.em_processo = False
            db.add(rastro)
            db.commit()
