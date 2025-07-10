import os
import requests
from sqlalchemy.orm import Session
from database import SessionLocal
from models.patch import PatchUpdate

def enviar_patches_pendentes():
    db: Session = SessionLocal()
    patches = db.query(PatchUpdate).filter(PatchUpdate.status != "enviado").all()

    if not patches:
        print("ℹ️ Nenhum patch pendente.")
        return

    for patch in patches:
        try:
            nfkey = patch.nfkey
            url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={nfkey}&courier_id=84"
            headers = {
                "Content-Type": "application/json-patch+json",
                "Authorization": os.getenv("TOUTBOX_API_KEY")
            }

            response = requests.patch(url, json=patch.payload, headers=headers)

            if response.status_code in [200, 204]:
                patch.status = "enviado"
                patch.response = response.text
                db.commit()
                print(f" PATCH enviado com sucesso: {nfkey}")
            else:
                patch.status = f"erro {response.status_code}"
                patch.response = response.text
                db.commit()
                print(f" Erro ao enviar PATCH {nfkey}: {response.status_code} - {response.text}")

        except Exception as e:
            print(f" Erro ao processar PATCH {patch.nfkey}: {e}")
    db.close()
