import os
import json
import requests
from sqlalchemy.orm import Session
from database import SessionLocal
from models.rastro import Rastro
from datetime import datetime


def montar_payload(rastro: Rastro):
    # GEO
    geo = None
    if rastro.geo_lat is not None and rastro.geo_long is not None:
        geo = {
            "lat": rastro.geo_lat,
            "long": rastro.geo_long
        }

    # FILES
    files = []
    if rastro.file_url:
        files = [{
            "url": rastro.file_url,
            "description": rastro.file_description or "",
            "fileType": rastro.file_type or ""
        }]

    # VALIDAÇÕES OBRIGATÓRIAS
    if not rastro.event_code:
        raise ValueError(f"RASTRO {rastro.nfkey} está com eventCode nulo. Corrija antes de enviar.")
    if not rastro.date:
        raise ValueError(f"RASTRO {rastro.nfkey} está com data nula. Corrija antes de enviar.")

    event = {
        "eventCode": rastro.event_code,
        "description": rastro.description or "",
        "date": rastro.date.isoformat(),
        "address": rastro.address,
        "number": rastro.number,
        "city": rastro.city,
        "state": rastro.state,
        "receiverDocument": rastro.receiver_document,
        "receiver": rastro.receiver,
        "geo": geo,
        "files": files if files else []
    }

    payload = {
        "nfKey": rastro.nfkey,
        "CourierId": rastro.courier_id,
        "events": [event],
        "orderId": rastro.order_id,  # Pode ir como None
        "additionalInfo": {
            "additionalProp1": "",
            "additionalProp2": "",
            "additionalProp3": ""
        },
        "trackingNumber": ""
    }

    return payload


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

            # Armazenar o payload como string válida
            rastro.payload = json.dumps(payload, ensure_ascii=False)
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
                print(f"🔥 Erro genérico ao processar rastro (objeto inválido): {e}")

    db.close()
