import os
import requests
from sqlalchemy.orm import Session
from database import SessionLocal
from models.rastro import Rastro

def montar_payload(rastro: Rastro):
    # Verifica se tem arquivo para anexar
    arquivos = []
    if rastro.file_url:
        arquivos.append({
            "url": rastro.file_url,
            "description": rastro.file_description or "",
            "fileType": rastro.file_type or "image/jpg"
        })

    evento = {
        "eventCode": rastro.event_code,
        "description": rastro.description,
        "date": rastro.date.isoformat() if rastro.date else None,
        "address": rastro.address,
        "number": rastro.number,
        "city": rastro.city,
        "state": rastro.state,
        "files": arquivos if arquivos else []
    }

    return {
        "nfKey": rastro.nfkey,
        "CourierId": rastro.courier_id,
        # ❌ Removido orderId porque está vindo como OV
        # "orderId": None,  ← opcional
        "trackingNumber": "",
        "additionalInfo": {
            "additionalProp1": "",
            "additionalProp2": "",
            "additionalProp3": ""
        },
        "events": [evento]
    }



def enviar_rastros_pendentes():
    db: Session = SessionLocal()
    rastros = db.query(Rastro).filter(Rastro.enviado == False).all()

    if not rastros:
        print("ℹ Nenhum rastro pendente.")
        return

    for rastro in rastros:
        try:
            payload = {"eventsData": [montar_payload(rastro)]}
            
            # ⚠️ Corrigido aqui: adicionar Bearer
            headers = {
                "Authorization": f"Bearer {os.getenv('TOUTBOX_API_KEY')}",
                "Content-Type": "application/json"
            }

            # ⚠️ Corrigido: endpoint oficial da Toutbox
            url = "https://production.toutbox.com.br/api/v1/External/Tracking"

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code in [200, 204]:
                rastro.enviado = True
                print(f"✅ RASTRO enviado com sucesso: {rastro.nfkey}")
            else:
                print(f"❌ Erro ao enviar RASTRO {rastro.nfkey}: {response.status_code} - {response.text}")
            
            db.commit()
        except Exception as e:
            print(f"🔥 Erro ao processar RASTRO {rastro.nfkey}: {e}")
    db.close()
