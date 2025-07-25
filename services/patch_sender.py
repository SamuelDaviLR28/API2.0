import httpx
import os
from database import SessionLocal
from models.historico_patch import HistoricoPatch

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
