from database import SessionLocal
from models.patch import PatchUpdate
from models.pedido import Pedido
from models.rastro import Rastro
from services.patch_sender import enviar_patch_para_toutbox, montar_payload_patch_com_sla
from services.rastro_sender import enviar_rastro_para_toutbox
from services.sla_service import buscar_sla
import json

async def processar_nfkey(nfkey: str):
    db = SessionLocal()
    try:
        patch = db.query(PatchUpdate).filter_by(nfkey=nfkey, status=None).first()
        if not patch:
            print(f"Nenhum patch pendente para nfkey {nfkey}")
            return

        pedido = db.query(Pedido).filter_by(nfkey=nfkey).first()
        if not pedido:
            print(f"Pedido não encontrado para nfkey {nfkey}")
            return

        sla_dias = buscar_sla(db, uf_origem=pedido.uf_remetente, uf_destino=pedido.uf_destinatario)
        if sla_dias is None:
            print(f"SLA não encontrado para {pedido.uf_remetente} -> {pedido.uf_destinatario}")
            return

        payload_patch = montar_payload_patch_com_sla(sla_dias)

        resultado_patch = await enviar_patch_para_toutbox(
            nfkey=nfkey,
            courier_id=patch.courier_id,
            payload=payload_patch
        )

        if resultado_patch["status"] != "enviado":
            print(f"Erro ao enviar patch para {nfkey}: {resultado_patch['response']}")
            return

        patch.status = 200
        patch.response = resultado_patch["response"]
        db.commit()

        rastros = db.query(Rastro).filter_by(nfkey=nfkey, enviado=False).all()
        for evento in rastros:
            item = {
                "nfKey": evento.nfkey,
                "events": [
                    {
                        "eventCode": evento.event_code,
                        "description": evento.description,
                        "date": evento.date,
                        "address": evento.address,
                        "number": evento.number,
                        "city": evento.city,
                        "state": evento.state,
                        "receiverDocument": evento.receiver_document,
                        "receiver": evento.receiver,
                        "geo": {
                            "lat": evento.geo_lat,
                            "lng": evento.geo_long,
                        },
                        "files": [{
                            "url": evento.file_url,
                            "description": evento.file_description,
                            "type": evento.file_type
                        }] if evento.file_url else []
                    }
                ],
                "CourierId": evento.courier_id
            }
            payload_rastro = {"eventsData": [item]}
            resultado_rastro = await enviar_rastro_para_toutbox(payload_rastro)

            evento.status = resultado_rastro["status"]
            evento.response = resultado_rastro["response"][:255]
            evento.payload = json.dumps(payload_rastro, ensure_ascii=False)
            evento.enviado = resultado_rastro["status"] == "enviado"
            db.commit()

        print(f"Processamento finalizado para nfkey {nfkey}")

    finally:
        db.close()


async def processar_todos_patches_e_rastros(db=None):
    # Se for passado db, usa ele; se não, cria um novo (para ser usado no route)
    criar_db = False
    if db is None:
        criar_db = True
        db = SessionLocal()
    try:
        patches_pendentes = db.query(PatchUpdate).filter(PatchUpdate.status.is_(None)).all()
        print(f"Encontrados {len(patches_pendentes)} patches pendentes")

        for patch in patches_pendentes:
            await processar_nfkey(patch.nfkey)
    finally:
        if criar_db:
            db.close()
