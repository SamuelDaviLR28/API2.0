from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List, Union
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models import Motorista

load_dotenv()

router = APIRouter(prefix="/hooks/vivo")

API_KEY = os.getenv("API_KEY")

# Exemplo de schema Motorista simplificado
class MotoristaSchema(BaseModel):
    nome: str
    cnh: str
    telefone: str
    # adicione aqui os campos que precisar...

async def get_db():
    async with SessionLocal() as session:
        yield session

async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key não fornecida")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key inválida")

@router.post("/motorista", dependencies=[Depends(verify_api_key)], status_code=201)
async def post_motorista(
    payload: Union[MotoristaSchema, List[MotoristaSchema]],  # aceita objeto ou lista
    db: AsyncSession = Depends(get_db)
):
    try:
        # Se for um único objeto, transforma em lista para facilitar
        if isinstance(payload, MotoristaSchema):
            payload = [payload]

        novos_motoristas = []
        for motorista_data in payload:
            novo = Motorista(dados=motorista_data.model_dump())
            db.add(novo)
            novos_motoristas.append(novo)

        await db.commit()

        # Atualiza os objetos com IDs gerados
        for novo in novos_motoristas:
            await db.refresh(novo)

        return {
            "message": f"{len(novos_motoristas)} motorista(s) registrado(s) com sucesso",
            "ids": [m.id for m in novos_motoristas],
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar dados do motorista: {e}")