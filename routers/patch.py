from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.patch import PatchUpdate
from models.pedido import Pedido
from services.sla_service import buscar_sla
from services.patch_sender import enviar_patch_para_toutbox, montar_payload_patch_com_sla
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/admin/verificar-patches")
async def verificar_e_ajustar_patches(db: Session = Depends(get_db)):
    patches_pendentes = db.query(PatchUpdate).filter(PatchUpdate.status.is_(None)).all()

    sem_pedido = []
    sem_sla = []
    ajustados = []

    for patch in patches_pendentes:
        pedido = db.query(Pedido).filter_by(nfkey=patch.nfkey).first()
        if not pedido:
            sem_pedido.append(patch.nfkey)
            continue

        sla_prazo = buscar_sla(db, uf_origem=pedido.uf_remetente, uf_destino=pedido.uf_destinatario)
        if sla_prazo is None:
            sem_sla.append({
                "nfkey": patch.nfkey,
                "uf_origem": pedido.uf_remetente,
                "uf_destino": pedido.uf_destinatario
            })
            continue

        payload = montar_payload_patch_com_sla(sla_prazo)
        patch.payload = json.dumps(payload)
        db.add(patch)
        ajustados.append(patch.nfkey)

    db.commit()

    resultados_envio = []
    for nfkey in ajustados:
        patch = db.query(PatchUpdate).filter_by(nfkey=nfkey).first()
        if patch:
            try:
                resultado = await enviar_patch_para_toutbox(
                    nfkey=patch.nfkey,
                    courier_id=patch.courier_id,
                    payload=json.loads(patch.payload)
                )
                patch.status = 200 if resultado['status'] == 'enviado' else None
                patch.response = resultado['response'][:255]
                db.add(patch)
                db.commit()
                resultados_envio.append({"nfkey": nfkey, "status": resultado['status']})
            except Exception as e:
                resultados_envio.append({"nfkey": nfkey, "erro": str(e)})

    return {
        "patches_sem_pedido": sem_pedido,
        "patches_sem_sla": sem_sla,
        "patches_ajustados": ajustados,
        "resultados_envio": resultados_envio
    }
