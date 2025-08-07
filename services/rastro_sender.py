import httpx
import os
import json
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro
from models.patch import PatchUpdate
from models.pedido import Pedido

load_dotenv()
TOUTBOX_API_URL = os.getenv("TOUTBOX_EVENT_API", "http://courier.toutbox.com.br/api/v1/Parcel/Event")
TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")

def montar_payload(evento: dict, nfkey: str, courier_id: int):
    event = {
        "geo": evento.get("geo"),
        "city": evento.get("city"),
        "date": evento.get("date"),
        "files": evento.get("files", []),
        "state": evento.get("state"),
        "number": evento.get("number"),
        "address": evento.get("address"),
        "receiver": evento.get("receiver"),
        "eventCode": evento.get("eventCode"),
        "description": evento.get("description"),
        "receiverDocument": evento.get("receiverDocument")
    }

    return {
        "eventsData": [
            {
                "nfKey": nfkey,
                "events": [event],
                "CourierId": courier_id
            }
        ]
    }

def enviar_rastros_pendentes(db: Session):
    pendentes = db.query(Rastro).filter(Rastro.status == "pendente").all()
    
    for rastro in pendentes:
        try:
            pedido = db.query(Pedido).filter(Pedido.nfkey == rastro.nfkey).first()
            if not pedido:
                rastro.status = "erro"
                rastro.response = "Pedido não encontrado"
                db.commit()
                continue

            payload_dict = json.loads(rastro.payload)
            events_data = payload_dict.get("eventsData", [])

            if not events_data or not events_data[0].get("events"):
                rastro.status = "erro"
                rastro.response = "Payload inválido ou sem eventos"
                db.commit()
                continue

            courier_id = events_data[0].get("CourierId")
            evento = events_data[0]["events"][0]

            payload_formatado = montar_payload(evento, rastro.nfkey, courier_id)

            headers = {
                "x-api-key": TOUTBOX_API_KEY,
                "Content-Type": "application/json"
            }

            response = httpx.post(
                TOUTBOX_API_URL,
                headers=headers,
                json=payload_formatado,
                timeout=20
            )

            rastro.status = "enviado" if response.status_code == 200 else f"erro {response.status_code}"
            rastro.response = response.text
            db.commit()

            historico = HistoricoRastro(
                nfkey=rastro.nfkey,
                payload=json.dumps(payload_formatado, ensure_ascii=False),
                status=rastro.status,
                response=response.text
            )
            db.add(historico)
            db.commit()

        except Exception as e:
            rastro.status = "erro"
            rastro.response = str(e)
            db.commit()
