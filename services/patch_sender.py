import os
import requests
from sqlalchemy.orm import Session
from database import SessionLocal
from models.patch import PatchUpdate

def enviar_patches_pendentes():
    db: Session = SessionLocal()
    patches = db.query(PatchUpdate).filter(PatchUpdate.status != "enviado").all()

    if not patches:
        print(" Nenhum patch pendente.")
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

            patch.response = response.text
            if response.status_code in [200, 204]:
                patch.status = "enviado"
                print(f" PATCH enviado com sucesso: {nfkey}")
            else:
                patch.status = f"erro {response.status_code}"
                print(f" Erro ao enviar PATCH {nfkey}: {response.status_code} - {response.text}")

            db.commit()

        except Exception as e:
            patch.status = 'erro'
            patch.response = str(e)
            db.commit()
            print(f" Erro ao processar PATCH {nfkey}: {e}")

    db.close()
