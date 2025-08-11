import json
import logging
import asyncio
import httpx
import os
from sqlalchemy.orm import Session
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TOUTBOX_API_URL_RASTRO = "http://courier.toutbox.com.br/api/v1/Parcel/Event"
TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")
MAX_TENTATIVAS = 5
BATCH_SIZE = 100
PAUSE_SECONDS = 1.0

def limpar_string(s):
    if s is None:
        return None
    return s.encode('utf-8', 'ignore').decode('utf-8', 'ignore')

def ajustar_eventos(events):
    for e in events:
        # Remove driver completamente
        e.pop("driver", None)

        # Limpa strings para evitar caracteres inválidos
        for campo in ["city", "address", "description", "number", "state"]:
            if campo in e and e[campo]:
                e[campo] = limpar_string(e[campo])

        # Ajusta files para [] se não houver URL válida
        if "files" in e:
            if not any(f.get("url") for f in e["files"]):
                e["files"] = []

        # Ajusta orderId para None se vazio ou inválido
        if "orderId" in e:
            if not e["orderId"]:
                e["orderId"] = None

    return events

def _normalize_payload_field(payload_field):
    if payload_field is None:
        return {}
    if isinstance(payload_field, (dict, list)):
        return payload_field
    try:
        return json.loads(payload_field)
    except Exception:
        try:
            return json.loads(str(payload_field))
        except Exception:
            return {}

def _extract_events_and_courier(payload_dict):
    events = []
    courier_id = None

    if "eventPayload" in payload_dict:
        ep = payload_dict.get("eventPayload")
        if isinstance(ep, list) and ep:
            block = ep[0]
            courier_id = block.get("courierId") or block.get("CourierId")
            events = block.get("events", [])
    elif "eventsData" in payload_dict:
        ed = payload_dict.get("eventsData")
        if isinstance(ed, list) and ed:
            block = ed[0]
            courier_id = block.get("courierId") or block.get("CourierId")
            events = block.get("events", [])
    return events or [], courier_id

def _montar_payload_toutbox(nfkey, courier_id, events):
    return {
        "eventsData": [
            {
                "nfKey": nfkey,
                "events": events,
                "CourierId": courier_id
            }
        ]
    }

async def enviar_rastro_para_toutbox(payload: dict):
    headers = {
        "Authorization": TOUTBOX_API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            logger.info(f"Enviando payload para Toutbox: {json.dumps(payload, ensure_ascii=False)}")
            response = await client.post(TOUTBOX_API_URL_RASTRO, json=payload, headers=headers)
        except Exception as e:
            logger.error(f"Erro conexão ao enviar rastro: {e}")
            return {"status": "erro conexao", "response": str(e)}

    if response.status_code in (200, 204):
        status = "enviado"
    else:
        status = f"erro {response.status_code}"
    return {"status": status, "response": response.text}

async def enviar_rastros_pendentes(db: Session):
    while True:
        rastros = db.query(Rastro).filter(
            ((Rastro.status == "pendente") | (Rastro.status.startswith("erro"))) &
            (Rastro.tentativas_envio < MAX_TENTATIVAS) &
            (Rastro.em_processo == False)
        ).order_by(Rastro.created_at).limit(BATCH_SIZE).all()

        if not rastros:
            logger.info("Nenhum rastro pendente encontrado.")
            break

        logger.info(f"Processando lote de {len(rastros)} rastros...")

        for rastro in rastros:
            try:
                rastro.em_processo = True
                rastro.tentativas_envio = (rastro.tentativas_envio or 0) + 1
                db.add(rastro)
                try:
                    db.commit()
                    db.refresh(rastro)
                except Exception as commit_err:
                    db.rollback()
                    logger.error(f"Erro no commit ao marcar rastro {rastro.id}: {commit_err}")
                    continue

                payload_dict = _normalize_payload_field(rastro.payload)
                events, courier_id = _extract_events_and_courier(payload_dict)

                eventos_validos = [e for e in events if e.get("eventCode") and str(e.get("eventCode")).strip()]
                if not eventos_validos:
                    rastro.status = "erro - sem eventCode"
                    rastro.response = f"Sem eventos com eventCode válido (tentativa {rastro.tentativas_envio})"
                    rastro.tentativas_envio = MAX_TENTATIVAS
                    rastro.em_processo = False
                    db.add(rastro)
                    try:
                        db.commit()
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Erro commit ao marcar sem eventCode rastro {rastro.id}: {e}")

                    try:
                        historico = HistoricoRastro(
                            nfkey=rastro.nfkey,
                            payload=json.dumps(payload_dict, ensure_ascii=False),
                            status=rastro.status,
                            response=rastro.response
                        )
                        db.add(historico)
                        db.commit()
                    except Exception:
                        db.rollback()
                    continue

                # Ajusta os eventos antes de montar o payload final
                eventos_validos = ajustar_eventos(eventos_validos)

                payload_corrigido = _montar_payload_toutbox(rastro.nfkey, courier_id, eventos_validos)
                resultado = await enviar_rastro_para_toutbox(payload_corrigido)

                rastro.status = resultado["status"]
                rastro.response = (resultado["response"] or "")[:2000]
                rastro.enviado = resultado["status"] == "enviado"
                rastro.em_processo = False
                db.add(rastro)
                try:
                    db.commit()
                    db.refresh(rastro)
                except Exception as commit_err:
                    db.rollback()
                    logger.error(f"Erro commit após envio rastro {rastro.id}: {commit_err}")

                try:
                    historico = HistoricoRastro(
                        nfkey=rastro.nfkey,
                        payload=json.dumps(payload_corrigido, ensure_ascii=False),
                        status=rastro.status,
                        response=resultado["response"]
                    )
                    db.add(historico)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.error(f"Erro ao salvar historico rastro {rastro.id}: {e}")

                await asyncio.sleep(0.2)

            except Exception as e:
                logger.exception(f"Erro ao processar rastro NFKey {rastro.nfkey}: {e}")
                try:
                    rastro.status = "erro"
                    rastro.response = str(e)[:2000]
                    rastro.em_processo = False
                    db.add(rastro)
                    db.commit()
                except Exception:
                    db.rollback()

        await asyncio.sleep(PAUSE_SECONDS)
