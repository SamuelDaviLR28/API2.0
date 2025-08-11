from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.patch_sender import enviar_patches_pendentes
from services.rastro_sender import enviar_rastros_pendentes

router = APIRouter()

@router.post("/integracao/enviar-pendentes")
async def enviar_pendentes_completos(db: Session = Depends(get_db)):
    # Enviar patches primeiro
    await enviar_patches_pendentes(db)
    # Depois enviar rastros apenas com patch enviado com sucesso
    await enviar_rastros_pendentes(db)
    return {"message": "Envio de patches e rastros pendentes concluído"}
