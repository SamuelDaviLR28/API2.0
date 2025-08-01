# routers/integracao.py
from fastapi import APIRouter, HTTPException
from services.integracao import processar_nfkey, processar_todos_patches_e_rastros
import asyncio

router = APIRouter()

@router.post("/processar-todos")
async def processar_todos():
    try:
        await processar_todos_patches_e_rastros()
        return {"message": "Processamento iniciado para todos patches pendentes."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
