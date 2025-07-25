import httpx
import os
import asyncio
from database import SessionLocal
from models.historico_patch import HistoricoPatch
from models.patch_update import PatchUpdate

async def enviar_patch_para_toutbox(nfkey: str, courier_id: int, payload: list):
    url = f"https://production.toutbox.com.br/api/v1/External/Order?nfkey={nfkey}&courier_id={courier_id}"
    headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": f"Bearer {os.getenv('TOUTBOX_API_KEY')}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.patch(url, json=payload, headers=headers)

    db = SessionLocal()
    status = "enviado" if response.status_code in [200, 204] else f"erro {response.status_code}"

    historico = HistoricoPatch(
        nfkey=nfkey,
        payload=payload,
        status=status,
        response=response.text
    )
    db.add(historico)

    # Atualiza status na tabela patch_updates
    patch = db.query(PatchUpdate).filter_by(nfkey=nfkey, courier_id=courier_id).first()
    if patch:
        patch.status = response.status_code
        patch.response = response.text
    db.commit()
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

def enviar_patches_pendentes():
    """Função síncrona para ser usada por agendador. Envia PATCHs pendentes."""
    db = SessionLocal()
    patches = db.query(PatchUpdate).filter(PatchUpdate.status.is_(None)).all()

    print(f"🕒 Iniciando envio de {len(patches)} patches pendentes...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for patch in patches:
        try:
            loop.run_until_complete(
                enviar_patch_para_toutbox(
                    nfkey=patch.nfkey,
                    courier_id=patch.courier_id,
                    payload=patch.payload
                )
            )
            print(f"✅ PATCH enviado para nfkey {patch.nfkey}")
        except Exception as e:
            print(f"❌ Erro ao enviar PATCH para nfkey {patch.nfkey}: {e}")
    db.close()
