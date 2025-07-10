import os
import requests
from sqlalchemy.orm import Session
from database import SessionLocal
from models.rastro import Rastro

def montar_payload(rastro: Rastro):
    return {
        "nfKey": rastro.nfkey,
        "CourierId": rastro.courier_id,
        "events": [{
            "eventCode": rastro.event_code,
            "description": rastro.description,
            "date": rastro.date.isoformat(),
            "address": rastro.address,
            "number": rastro.number,
            "city": rastro.city,
            "state": rastro.state,
            "receiverDocument": rastro.receiver_document,
            "receiver": rastro.receiver,
            "geo": {
                "lat": rastro.geo_lat,
                "_long": rastro.geo_long
            },
            "files": [{
                "url": rastro.file_url,
                "description": rastro.file_description,
                "fileType": rastro.file_type
            }] if rastro.file_url else []
        }]
    }

def enviar_rastros_pendentes():
    db: Session = SessionLocal()
    rastros = db.query(Rastro).filter(Rastro.enviado == False).all()

    if not rastros:
        print("ℹ️ Nenhum rastro pendente.")
        return

    for rastro in rastros:
        try:
            payload = {"eventsData": [montar_payload(rastro)]}
            headers = {
                "Authorization": os.getenv("TOUTBOX_API_KEY"),
                "Content-Type": "application/json"
            }
            url = "http://courier.toutbox.com.br/api/v1/Parcel/Event"
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code in [200, 204]:
                rastro.enviado = True
                db.commit()
                print(f" RASTRO enviado com sucesso: {rastro.nfkey}")
            else:
                print(f" Erro ao enviar RASTRO {rastro.nfkey}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f" Erro ao processar RASTRO {rastro.nfkey}: {e}")
    db.close()
