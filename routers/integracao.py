from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.integracao import processar_todos_patches_e_rastros

router = APIRouter()

@router.post("/integracao/enviar-pendentes")
async def enviar_pendentes_completos(db: Session = Depends(get_db)):
    # Enviar patches e depois rastros vinculados, garantindo ordem
    await processar_todos_patches_e_rastros(db)
    return {"message": "Envio de patches e rastros pendentes concluído"}
