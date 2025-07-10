import requests
from database import SessionLocal
from models.dispatch import Dispatch

ESL_DISPATCH_URL = "https://link-da-esl.com/api/dispatch"  # atualize com o real

def enviar_dispatch_para_esl():
    db = SessionLocal()
    try:
        pedidos_pendentes = db.query(Dispatch).filter(Dispatch.status == 'pendente').all()
        for pedido in pedidos_pendentes:
            try:
                response = requests.post(ESL_DISPATCH_URL, json=pedido.payload)
                if response.status_code == 200:
                    pedido.status = 'enviado'
                else:
                    pedido.status = 'erro'
                    pedido.response = response.text
            except Exception as e:
                pedido.status = 'erro'
                pedido.response = str(e)
            finally:
                db.commit()
    finally:
        db.close()
