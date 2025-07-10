import requests
import json
from database import SessionLocal
from models.pedido import Pedido  # ← Modelo correto

ESL_DISPATCH_URL = "https://link-da-esl.com/api/dispatch"  # Substitua pelo link real

def enviar_dispatch_para_esl():
    db = SessionLocal()
    try:
        pedidos_pendentes = db.query(Pedido).filter(Pedido.status == 'pendente').all()

        if not pedidos_pendentes:
            print("ℹ️ Nenhum dispatch pendente para enviar ao ESL.")
            return

        for pedido in pedidos_pendentes:
            try:
                response = requests.post(
                    ESL_DISPATCH_URL,
                    json=json.loads(pedido.json_completo)
                )

                if response.status_code in [200, 201]:
                    pedido.status = 'enviado'
                    print(f"✅ Dispatch enviado: {pedido.numero_pedido}")
                else:
                    pedido.status = 'erro'
                    pedido.response = response.text
                    print(f"❌ Erro no dispatch {pedido.numero_pedido}: {response.status_code} - {response.text}")

            except Exception as e:
                pedido.status = 'erro'
                pedido.response = str(e)
                print(f"🔥 Exceção no envio do dispatch {pedido.numero_pedido}: {e}")

            finally:
                db.commit()

    finally:
        db.close()
