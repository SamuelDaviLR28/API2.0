import json
import logging
import traceback
import httpx
import os
from sqlalchemy.orm import Session
from models.patch import PatchUpdate
from models.pedido import Pedido
from models.historico_patch import HistoricoPatch
from services.sla_service import buscar_sla
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")
TOUTBOX_API_URL_PATCH = "https://production.toutbox.com.br/api/v1/External/Order"

async def enviar_patch_para_toutbox(nfkey: str, courier_id: int, payload: list, db: Session):
    url = f"{TOUTBOX_API_URL_PATCH}?nfkey={nfkey}&courier_id={courier_id}"
    headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": TOUTBOX_API_KEY
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.patch(url, json=payload, headers=headers)
    except Exception as e:
        logger.error(f"Erro PATCH nfkey {nfkey}: {e}")
        return {"status": "erro", "response": str(e)}

    status_code = response.status_code
    status = "enviado" if status_code in [200, 204] else f"erro {status_code}"

    try:
        historico = HistoricoPatch(
            nfkey=nfkey,
            payload=json.dumps(payload, ensure_ascii=False),
            status=status,
            response=response.text[:255]
        )
        db.add(historico)

        patch = db.query(PatchUpdate).filter_by(nfkey=nfkey, courier_id=courier_id).first()
        if patch:
            patch.status = status_code
            patch.response = response.text
            db.add(patch)
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao salvar histórico PATCH nfkey {nfkey}: {e}")
        db.rollback()

    return {"status": status, "response": response.text}

def montar_payload_patch_com_sla(prazo_dias_uteis: int) -> list:
    return [
        {
            "op": "replace",
            "path": "/Itens/0/Frete/Transportadora/PrazoDiasUteis",
            "value": str(prazo_dias_uteis)
        }
    ]

async def enviar_patches_pendentes(db: Session):
    patches = db.query(PatchUpdate).filter(
        PatchUpdate.status.is_(None)
    ).all()

    logger.info(f"Enviando {len(patches)} patches pendentes...")

    for patch in patches:
        try:
            pedido = db.query(Pedido).filter_by(nfkey=patch.nfkey).first()
            if not pedido:
                logger.warning(f"Pedido não encontrado para nfkey {patch.nfkey}")
                patch.status = -1
                patch.response = "Pedido não encontrado"
                db.add(patch)
                db.commit()
                continue

            sla_dias = buscar_sla(db, uf_origem=pedido.uf_remetente, uf_destino=pedido.uf_destinatario)
            if sla_dias is None:
                logger.warning(f"SLA não encontrado para rota {pedido.uf_remetente} -> {pedido.uf_destinatario}")
                patch.status = -2
                patch.response = "SLA não encontrado"
                db.add(patch)
                db.commit()
                continue

            payload = montar_payload_patch_com_sla(sla_dias)
            patch.payload = json.dumps(payload, ensure_ascii=False)
            db.add(patch)
            db.commit()

            resultado = await enviar_patch_para_toutbox(patch.nfkey, patch.courier_id, payload, db)
            logger.info(f"PATCH nfkey {patch.nfkey} resultado: {resultado['status']}")

        except Exception:
            logger.exception(f"Erro no envio PATCH nfkey {patch.nfkey}")
            db.rollback()
