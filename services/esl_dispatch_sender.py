import os
import json
import requests
from database import SessionLocal
from models.pedido import Pedido

ESL_DISPATCH_URL = "https://import.eslcloud.com.br/v1/TransportRequests"

def enviar_dispatch_para_esl():
    db = SessionLocal()
    try:
        pedidos_pendentes = db.query(Pedido).filter(Pedido.status == 'pendente').all()

        if not pedidos_pendentes:
            print("ℹ Nenhum dispatch pendente para enviar ao ESL.")
            return

        for pedido in pedidos_pendentes:
            try:
                response = requests.post(
                    ESL_DISPATCH_URL,
                    json=json.loads(pedido.json_completo),
                    headers={
                        "Authorization": os.getenv("ESL_API_KEY"),
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code in [200, 201]:
                    pedido.status = 'enviado'
                    print(f" Dispatch enviado: {pedido.numero_pedido}")
                else:
                    pedido.status = 'erro'
                    pedido.response = response.text
                    print(f" Erro no dispatch {pedido.numero_pedido}: {response.status_code} - {response.text}")
                db.commit()

            except Exception as e:
                pedido.status = 'erro'
                pedido.response = str(e)
                db.commit()
                print(f" Exceção no envio do dispatch {pedido.numero_pedido}: {e}")
    finally:
        db.close()
