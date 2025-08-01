import httpx
import os
import json
from database import SessionLocal
from models.historico_patch import HistoricoPatch
from models.patch import PatchUpdate
from models.pedido import Pedido
from services.sla_service import buscar_sla
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

async def enviar_patch_para_toutbox(nfkey: str, courier_id: int, payload: list):
    url = f"https://production.toutbox.com.br/api/v1/External/Order?nfkey={nfkey}&courier_id={courier_id}"

    headers = {
        "Content-Type": "application/json-patch+json",
        "Authentication": os.getenv("TOUTBOX_API_KEY")  # ✅ Corrigido para Authentication
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.patch(url, json=payload, headers=headers)
    except Exception as e:
        return {
            "nfkey": nfkey,
            "status": "erro - exceção na requisição",
            "response": str(e)
        }

    status = "enviado" if response.status_code in [200, 204] else f"erro {response.status_code}"

    db = SessionLocal()
    try:
        historico = HistoricoPatch(
            nfkey=nfkey,
            payload=json.dumps(payload),
            status=status,
            response=response.text[:255]
        )
        db.add(historico)

        patch = db.query(PatchUpdate).filter_by(nfkey=nfkey, courier_id=courier_id).first()
        if patch:
            patch.status = response.status_code
            patch.response = response.text

        db.commit()
    finally:
        db.close()

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
    patches = db.query(PatchUpdate).filter(PatchUpdate.status.is_(None)).all()
    print(f"🕒 Enviando {len(patches)} patches pendentes...")

    for patch in patches:
        pedido = db.query(Pedido).filter_by(nfkey=patch.nfkey).first()

        if not pedido:
            print(f"⚠️ Pedido não encontrado para nfkey {patch.nfkey}")
            continue

        sla_dias = buscar_sla(db, uf_origem=pedido.uf_remetente, uf_destino=pedido.uf_destinatario)

        if sla_dias is None:
            print(f"⚠️ SLA não encontrado para {pedido.uf_remetente} -> {pedido.uf_destinatario}")
            continue

        payload = montar_payload_patch_com_sla(sla_dias)

        try:
            resultado = await enviar_patch_para_toutbox(
                nfkey=patch.nfkey,
                courier_id=patch.courier_id,
                payload=payload
            )
            print(f"✅ PATCH enviado para nfkey {patch.nfkey}: {resultado['status']}")
        except Exception as e:
            print(f"❌ Erro ao enviar PATCH para nfkey {patch.nfkey}: {e}")

    db.close()
