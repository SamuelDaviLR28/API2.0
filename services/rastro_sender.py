import httpx
import os
import json
from dotenv import load_dotenv
from database import SessionLocal
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro
from models.patch import PatchUpdate
from models.pedido import Pedido  



load_dotenv()

TOUTBOX_URL = os.getenv("TOUTBOX_EVENT_URL", "http://courier.toutbox.com.br/api/v1/Parcel/Event")
TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")


def montar_payload_toutbox(rastro: Rastro, pedido: Pedido):
    try:
        # Extrair payload original (conforme salvo no banco)
        dados_evento = json.loads(rastro.payload)

        eventos = dados_evento.get("events", [])
        if not eventos:
            raise ValueError("Evento sem conteúdo válido.")

        evento_formatado = []
        for evento in eventos:
            evento_formatado.append({
                "eventCode": evento.get("eventCode"),
                "date": evento.get("date"),
                "city": evento.get("city"),
                "state": evento.get("state"),
                "number": evento.get("number"),
                "address": evento.get("address"),
                "description": evento.get("description", ""),
                "receiver": evento.get("receiver", None),
                "files": evento.get("files", []),  # deve ser array, vazio se não houver imagens
            })

        payload = {
            "eventsData": [
                {
                    "CourierId": rastro.courier_id or 0,
                    "nfKey": rastro.nfkey,
                    "orderId": None,
                    "trackingNumber": "",
                    "events": evento_formatado,
                    "additionalInfo": {
                        "additionalProp1": "",
                        "additionalProp2": "",
                        "additionalProp3": ""
                    }
                }
            ]
        }

        return payload
    except Exception as e:
        raise ValueError(f"Erro ao montar payload: {str(e)}")


def enviar_rastros_pendentes(db: Session):
    rastros_pendentes = db.query(Rastro).filter(Rastro.status == "pendente").all()

    for rastro in rastros_pendentes:
        try:
            pedido = db.query(Pedido).filter(Pedido.nfkey == rastro.nfkey).first()
            if not pedido:
                rastro.status = "erro"
                rastro.response = "Pedido não encontrado."
                db.commit()
                continue

            payload = montar_payload_toutbox(rastro, pedido)

            headers = {
                "Content-Type": "application/json",
                "x-api-key": TOUTBOX_API_KEY
            }

            response = requests.post(TOUTBOX_URL, json=payload, headers=headers)

            rastro.response = response.text
            if response.status_code == 200:
                rastro.status = "enviado"
            else:
                rastro.status = f"erro {response.status_code}"

            # Salva histórico
            historico = HistoricoRastro(
                nfkey=rastro.nfkey,
                courier_id=rastro.courier_id,
                payload=json.dumps(payload, ensure_ascii=False),
                status=rastro.status,
                response=response.text
            )
            db.add(historico)
            db.commit()

        except Exception as e:
            rastro.status = "erro"
            rastro.response = str(e)
            db.commit()


