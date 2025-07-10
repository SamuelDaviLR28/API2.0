import requests
from database import SessionLocal
from models.dispatch import Dispatch

ESL_DISPATCH_URL = "https://link-da-esl.com/api/dispatch"  # Substitua pelo link real

def enviar_dispatch_para_esl():
    db = SessionLocal()
    try:
        pedidos_pendentes = db.query(Dispatch).filter(Dispatch.status == 'pendente').all()

        if not pedidos_pendentes:
            print("ℹ️ Nenhum dispatch pendente para enviar ao ESL.")
            return

        for pedido in pedidos_pendentes:
            try:
                response = requests.post(ESL_DISPATCH_URL, json=pedido.payload)

                if response.status_code in [200, 201]:
                    pedido.status = 'enviado'
                    print(f"✅ Dispatch enviado: {pedido.order_id}")
                else:
                    pedido.status = 'erro'
                    pedido.response = response.text
                    print(f"❌ Erro no dispatch {pedido.order_id}: {response.status_code} - {response.text}")

            except Exception as e:
                pedido.status = 'erro'
                pedido.response = str(e)
                print(f"🔥 Exceção no envio do dispatch {pedido.order_id}: {e}")

            finally:
                db.commit()

    finally:
        db.close()
