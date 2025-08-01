from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.integracao import processar_todos_patches_e_rastros

router = APIRouter()

@router.post("/admin/enviar-patches-rastros-pendentes")
async def enviar_patches_rastros_pendentes(db: Session = Depends(get_db)):
    try:
        await processar_todos_patches_e_rastros()
        return {"status": "sucesso", "mensagem": "Todos patches e rastros pendentes foram enviados."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar patches e rastros: {e}")
