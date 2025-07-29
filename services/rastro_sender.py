# services/rastro_sender.py

import httpx
import os
import json
from database import SessionLocal
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro

async def enviar_rastro_para_toutbox(payload: dict, courier_id: int):
    url = "http://courier.toutbox.com.br/api/v1/Parcel/Event"  # Atualizado
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('TOUTBOX_API_KEY')}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

    status = "enviado" if response.status_code in [200, 204] else f"erro {response.status_code}"

    db = SessionLocal()
    historico = HistoricoRastro(
        nfkey=payload["nfKey"],
        payload=json.dumps(payload),
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
    geo = None
    if evento.geo_lat and evento.geo_long:
        geo = {"lat": evento.geo_lat, "long": evento.geo_long}

    files = []
    if evento.file_url:
        files.append({
            "url": evento.file_url,
            "description": evento.file_description or "",
            "type": evento.file_type or "OUTRO"
        })

    return {
        "nfKey": evento.nfkey,
        "CourierId": evento.courier_id,
        "events": [{
            "eventCode": evento.event_code,
            "description": evento.description or "",
            "date": evento.date.isoformat() if evento.date else None,
            "address": evento.address,
            "number": evento.number,
            "city": evento.city,
            "state": evento.state,
            "receiverDocument": evento.receiver_document,
            "receiver": evento.receiver,
            "geo": geo,
            "files": files
        }]
    }

# ESTA É A FUNÇÃO QUE DEVE EXISTIR PARA EVITAR O ERRO
async def enviar_rastros_pendentes():
    db = SessionLocal()
    eventos = db.query(Rastro).filter(Rastro.enviado == False).all()

    for evento in eventos:
        payload = montar_payload_rastro(evento)
        resultado = await enviar_rastro_para_toutbox(payload, evento.courier_id)

        evento.status = resultado["status"]
        evento.response = resultado["response"]
        evento.payload = json.dumps(payload)
        evento.enviado = resultado["status"] == "enviado"

    db.commit()
    db.close()
