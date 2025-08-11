import httpx
import os
import json
import traceback
from database import SessionLocal
from models.historico_patch import HistoricoPatch
from models.patch import PatchUpdate
from models.pedido import Pedido
from services.sla_service import buscar_sla
from dotenv import load_dotenv

load_dotenv()

TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY", "").strip()
MAX_TENTATIVAS = 5

async def enviar_patch_para_toutbox(nfkey: str, courier_id: int, payload: list):
    url = f"https://production.toutbox.com.br/api/v1/External/Order?nfkey={nfkey}&courier_id={courier_id}"

    headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": TOUTBOX_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.patch(url, json=payload, headers=headers)
    except Exception as e:
        return {
            "nfkey": nfkey,
            "status": "erro - exceção na requisição",
            "response": str(e)
        }

    status = "enviado" if response.status_code in [200, 204] else f"erro {response.status_code}"

    return {
        "nfkey": nfkey,
        "status": status,
        "response": response.text
    }

def montar_payload_patch_com_sla(prazo_dias_uteis: int) -> list:
    return [
        {
            "op": "replace",
            "path": "/Itens/0/Frete/Transportadora/PrazoDiasUteis",
            "value": str(prazo_dias_uteis)
        }
    ]

async def enviar_patches_pendentes():
    db = SessionLocal()
    try:
        patches = db.query(PatchUpdate).filter(
            (PatchUpdate.status.is_(None)) | 
            ((PatchUpdate.status != 200) & (PatchUpdate.tentativas_envio < MAX_TENTATIVAS))
        ).all()

        for patch in patches:
            try:
                pedido = db.query(Pedido).filter_by(nfkey=patch.nfkey).first()
                if not pedido:
                    patch.status = -1
                    patch.response = "Pedido não encontrado"
                    db.add(patch)
                    db.commit()
                    continue

                sla_dias = buscar_sla(db, uf_origem=pedido.uf_remetente, uf_destino=pedido.uf_destinatario)
                if sla_dias is None:
                    patch.status = -2
                    patch.response = "SLA não encontrado"
                    db.add(patch)
                    db.commit()
                    continue

                payload = montar_payload_patch_com_sla(sla_dias)
                patch.payload = json.dumps(payload, ensure_ascii=False)
                patch.tentativas_envio += 1

                resultado = await enviar_patch_para_toutbox(
                    nfkey=patch.nfkey,
                    courier_id=patch.courier_id,
                    payload=payload
                )

                patch.status = 200 if resultado['status'] == 'enviado' else None
                patch.response = resultado['response'][:255]
                db.add(patch)

                historico = HistoricoPatch(
                    nfkey=patch.nfkey,
                    payload=json.dumps(payload, ensure_ascii=False),
                    status=resultado['status'],
                    response=resultado['response'][:255]
                )
                db.add(historico)

                db.commit()

            except Exception as e:
                patch.status = -3
                patch.response = f"Erro interno: {str(e)}"
                db.add(patch)
                db.commit()

    finally:
        db.close()
