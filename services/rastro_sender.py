import os
import json
import requests
from sqlalchemy.orm import Session
from database import SessionLocal
from models.rastro import Rastro
from datetime import datetime


def montar_payload(rastro: Rastro):
    # Geo: enviar null se não houver coordenadas
    geo = None
    if rastro.geo_lat is not None and rastro.geo_long is not None:
        geo = {
            "lat": rastro.geo_lat,
            "long": rastro.geo_long
        }

    # Files: enviar [] se não tiver URL
    files = []
    if rastro.file_url:
        files.append({
            "url": rastro.file_url,
            "description": rastro.file_description or "",
            "fileType": rastro.file_type or ""
        })

    # Validação de campos obrigatórios
    if not rastro.event_code:
        raise ValueError(f"RASTRO {rastro.nfkey} está com eventCode nulo. Corrija antes de enviar.")
    if not rastro.date:
        raise ValueError(f"RASTRO {rastro.nfkey} está com data nula. Corrija antes de enviar.")

    event = {
        "eventCode": rastro.event_code,
        "description": rastro.description or "",
        "date": rastro.date.isoformat(),  # Obrigatório no formato ISO
        "address": rastro.address or "",
        "number": rastro.number or "",
        "city": rastro.city or "",
        "state": rastro.state or "",
        "receiverDocument": rastro.receiver_document or "",
        "receiver": rastro.receiver or "",
        "geo": geo,
        "files": files
    }

    evento_dict = {
        "nfKey": rastro.nfkey,
        "CourierId": rastro.courier_id,
        "events": [event]
    }

    # orderId é opcional — enviar apenas se existir
    if rastro.order_id:
        evento_dict["orderId"] = rastro.order_id
    else:
        evento_dict["orderId"] = None

    return evento_dict


def enviar_rastros_pendentes():
    db: Session = SessionLocal()
    rastros = db.query(Rastro).filter(Rastro.enviado == False).all()

    if not rastros:
        print("ℹ Nenhum rastro pendente.")
        return

    for rastro in rastros:
        try:
            payload_dict = montar_payload(rastro)
            payload = {"eventsData": [payload_dict]}

            headers = {
                "Authorization": f"Bearer {os.getenv('TOUTBOX_API_KEY')}",
                "Content-Type": "application/json"
            }

            url = "https://production.toutbox.com.br/api/v1/External/Tracking"

            response = requests.post(url, json=payload, headers=headers)

            # Serializar corretamente como JSON
            rastro.payload = json.dumps(payload)
            rastro.updated_at = datetime.utcnow()

            if response.status_code in [200, 204]:
                rastro.enviado = True
                rastro.status = "sucesso"
                rastro.response = response.text
                print(f"✅ RASTRO enviado com sucesso: {rastro.nfkey}")
            else:
                rastro.status = "erro"
                rastro.response = response.text
                print(f"❌ Erro ao enviar RASTRO {rastro.nfkey}: {response.status_code} - {response.text}")

            db.commit()

        except Exception as e:
            db.rollback()
            try:
                print(f"🔥 Erro ao processar RASTRO {rastro.nfkey}: {e}")
            except:
                print(f"🔥 Erro genérico ao processar rastro (provavelmente o objeto foi invalidado): {e}")

    db.close()
