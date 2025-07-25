from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.pedido import Pedido
from services.sla_service import buscar_sla
from services.patch_sender import montar_payload_patch_com_sla, enviar_patch_para_toutbox
import os

router = APIRouter()

@router.patch("/patch")
async def enviar_patch(
    nfkey: str,
    courier_id: int = 84,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    API_KEY = os.getenv("API_KEY")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Chave de API inválida.")

    pedido = db.query(Pedido).filter(Pedido.nfkey == nfkey).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    sla_prazo = buscar_sla(db, uf_origem=pedido.uf_origem, uf_destino=pedido.uf_destino, cidade_destino=pedido.cidade_destino)
    if sla_prazo is None:
        sla_prazo = 3  # padrão caso não encontrado

    payload_patch = montar_payload_patch_com_sla(sla_prazo)

    result = await enviar_patch_para_toutbox(nfkey, courier_id, payload_patch)

    return result
