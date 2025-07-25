import httpx
import os
from database import SessionLocal
from models.historico_rastro import HistoricoRastro

async def enviar_rastro_para_toutbox(payload: dict, courier_id: int):
    url = f"https://production.toutbox.com.br/api/v1/External/Tracking"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('TOUTBOX_API_KEY')}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

    db = SessionLocal()
    status = "enviado" if response.status_code in [200, 204] else f"erro {response.status_code}"

    historico = HistoricoRastro(
        nfkey=payload["nfKey"],
        payload=payload,
        status=status,
        response=response.text
    )
    db.add(historico)
    db.commit()
    db.close()

    return {
        "nfkey": payload["nfKey"],
        "status": status,
        "response": response.text
    }

def montar_payload_rastro(evento) -> dict:
    # montar o payload de acordo com seus campos do Evento e regras de negócio
    return {
        "nfKey": evento.nfkey,
        "CourierId": evento.courier_id,
        "events": [
            {
                "eventCode": evento.event_code,
                "description": evento.description or "",
                "date": evento.date.isoformat(),
                "address": evento.address,
                "number": evento.number,
                "city": evento.city,
                "state": evento.state,
                "receiverDocument": evento.receiver_document,
                "receiver": evento.receiver,
                "geo": evento.geo or None,
                "files": evento.files or [],
            }
        ]
    }
