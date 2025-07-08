import os
import requests
from sqlalchemy.orm import Session
from database import SessionLocal
from models.patch import Patch

def enviar_patches_pendentes():
    db: Session = SessionLocal()
    patches = db.query(Patch).filter(Patch.enviado == False).all()

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
                patch.enviado = True
                db.commit()
                print(f"✅ PATCH enviado com sucesso: {nfkey}")
            else:
                print(f"❌ Erro ao enviar PATCH {nfkey}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"🔥 Erro ao processar PATCH {patch.nfkey}: {e}")
    db.close()
