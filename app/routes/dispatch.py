from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os

from app.database import SessionLocal
from app.models import Dispatch
from app.schemas.dispatch import DispatchToutbox

router = APIRouter(prefix="/hooks/vivo")
API_KEY = os.getenv("API_KEY")


async def get_db():
    async with SessionLocal() as session:
        yield session


async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API Key inválida")


@router.post("/dispatch", dependencies=[Depends(verify_api_key)], status_code=201)
async def receive_dispatch(
    payload: DispatchToutbox,
    db: AsyncSession = Depends(get_db)
):
    unique_id = payload.NumeroPedidoErp
    if unique_id:
        q = select(Dispatch).filter(Dispatch.unique_id == unique_id)
        res = await db.execute(q)
        if res.scalars().first():
            return {"message": "Dispatch já cadastrado", "unique_id": unique_id}

    order_id = payload.NumeroPedido
    canal_de_venda = payload.CanalDeVenda
    itens = payload.Itens or []

    destinatario = None
    remetente = None
    nota_fiscal = None
    infos_adicionais = None

    dispatch_data = {
        "order_id": order_id,
        "unique_id": unique_id,
        "client_info": jsonable_encoder(canal_de_venda),
        "recipient_info": jsonable_encoder(destinatario),
        "invoice_info": jsonable_encoder(nota_fiscal),
        "origin_info": jsonable_encoder(remetente),
        "volumes": jsonable_encoder(itens),
    }

    novo = Dispatch(**dispatch_data)
    db.add(novo)
    await db.commit()
    await db.refresh(novo)

    return {"message": "Pedido recebido com sucesso", "id": novo.id}