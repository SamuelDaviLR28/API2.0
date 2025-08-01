from database import SessionLocal
from services.patch_sender import enviar_patch_para_toutbox, montar_payload_patch_com_sla
from services.rastro_sender import enviar_rastro_para_toutbox, montar_payload_rastro
from services.sla_service import buscar_sla
from models.patch import PatchUpdate
from models.pedido import Pedido
from models.rastro import Rastro
import json
import asyncio

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
            item = montar_payload_rastro(evento)
            payload_rastro = {"eventsData": [item]}
            resultado_rastro = await enviar_rastro_para_toutbox(payload_rastro, evento.courier_id)

            evento.status = resultado_rastro["status"]
            evento.response = resultado_rastro["response"][:255]
            evento.payload = json.dumps(payload_rastro)
            evento.enviado = resultado_rastro["status"] == "enviado"
            db.commit()

        print(f"Processamento finalizado para nfkey {nfkey}")

    finally:
        db.close()

async def processar_todos_patches_e_rastros():
    db = SessionLocal()
    try:
        patches_pendentes = db.query(PatchUpdate).filter(PatchUpdate.status.is_(None)).all()
        print(f"Encontrados {len(patches_pendentes)} patches pendentes")

        for patch in patches_pendentes:
            await processar_nfkey(patch.nfkey)
    finally:
        db.close()
