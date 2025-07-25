import os
import requests
from sqlalchemy.orm import Session
from database import SessionLocal
from models.patch import PatchUpdate

def enviar_rastros_pendentes():
    db: Session = SessionLocal()
    rastros = db.query(Rastro).filter(Rastro.enviado == False).all()

    if not rastros:
        print("ℹ Nenhum rastro pendente.")
        return

    for rastro in rastros:
        # ✅ Verifica se o PATCH foi enviado com sucesso
        patch_ok = (
            db.query(PatchUpdate)
            .filter(
                PatchUpdate.nfkey == rastro.nfkey,
                PatchUpdate.status == "enviado"
            )
            .first()
        )
        if not patch_ok:
            print(f"⏸ Aguardando PATCH da nfkey {rastro.nfkey}. Rastro não será enviado ainda.")
            continue

        try:
            payload_dict = montar_payload(rastro)
            payload = {"eventsData": [payload_dict]}

            headers = {
                "Authorization": f"Bearer {os.getenv('TOUTBOX_API_KEY')}",
                "Content-Type": "application/json"
            }

            url = "https://production.toutbox.com.br/api/v1/External/Tracking"
            response = requests.post(url, json=payload, headers=headers)

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
            print(f"🔥 Erro ao processar RASTRO {rastro.nfkey}: {e}")

    db.close()
