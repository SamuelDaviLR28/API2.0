import json
import logging
import asyncio
import httpx
from sqlalchemy.orm import Session
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

TOUTBOX_API_URL_RASTRO = "http://courier.toutbox.com.br/api/v1/Parcel/Event"
TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")
MAX_TENTATIVAS = 5

async def enviar_rastro_para_toutbox(payload: dict):
    headers = {
        "Authorization": TOUTBOX_API_KEY,
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
    rastros = db.query(Rastro).filter(
        ((Rastro.status == "pendente") | (Rastro.status.startswith("erro"))) &
        (Rastro.tentativas_envio < MAX_TENTATIVAS) &
        (Rastro.em_processo == False)
    ).all()

    logger.info(f"Enviando {len(rastros)} rastros pendentes...")

    for rastro in rastros:
        try:
            rastro.em_processo = True
            rastro.tentativas_envio = (rastro.tentativas_envio or 0) + 1
            db.add(rastro)
            db.commit()
            db.refresh(rastro)

            payload_dict = json.loads(rastro.payload)
            # Extrair dados da estrutura antiga ou aceitar apenas o payload salvo, mas montar o payload novo abaixo
            events = []
            courier_id = None

            # Detectar se payload tem eventPayload (em caso de reenvio) ou eventsData (recebimento original)
            if "eventPayload" in payload_dict:
                ep = payload_dict["eventPayload"]
                if ep and isinstance(ep, list):
                    courier_id = ep[0].get("courierId")
                    events = ep[0].get("events", [])
            elif "eventsData" in payload_dict:
                ed = payload_dict["eventsData"]
                if ed and isinstance(ed, list):
                    courier_id = ed[0].get("CourierId")
                    events = ed[0].get("events", [])
            else:
                raise ValueError("Payload não contém 'eventPayload' nem 'eventsData'")

            # Validar eventCode de cada evento
            eventos_validos = [e for e in events if e.get("eventCode") and e.get("eventCode").strip()]
            if not eventos_validos:
                raise ValueError(f"Todos os eventos sem eventCode válido para nfkey {rastro.nfkey}")

            # Montar o payload correto para Toutbox
            payload_corrigido = {
                "eventPayload": [
                    {
                        "trackingNumber": None,
                        "orderId": None,
                        "nfKey": rastro.nfkey,
                        "uniqueId": None,
                        "courierId": courier_id,
                        "iccids": None,
                        "additionalInfo": None,
                        "events": eventos_validos,
                    }
                ]
            }

            resultado = await enviar_rastro_para_toutbox(payload_corrigido)

            rastro.status = resultado["status"]
            rastro.response = resultado["response"]
            rastro.enviado = resultado["status"] == "enviado"
            rastro.em_processo = False
            db.add(rastro)
            db.commit()
            db.refresh(rastro)

            # Salvar histórico
            historico = HistoricoRastro(
                nfkey=rastro.nfkey,
                payload=json.dumps(payload_corrigido, ensure_ascii=False),
                status=rastro.status,
                response=resultado["response"]
            )
            db.add(historico)
            db.commit()

            await asyncio.sleep(0.5)  # para evitar bursts excessivos

        except Exception as e:
            logger.exception(f"Erro ao enviar rastro NFKey {rastro.nfkey}: {e}")
            rastro.status = "erro"
            rastro.response = str(e)
            rastro.em_processo = False
            db.add(rastro)
            db.commit()
