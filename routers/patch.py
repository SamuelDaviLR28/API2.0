from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.patch import PatchUpdate
from services.patch_sender import enviar_patches_pendentes

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.patch("/patch")
async def registrar_patch(
    nfkey: str,
    courier_id: int,
    db: Session = Depends(get_db)
):
    existente = db.query(PatchUpdate).filter_by(nfkey=nfkey, courier_id=courier_id, status=None).first()
    if existente:
        return {"message": "Patch já registrado e pendente de envio.", "id": existente.id}

    novo_patch = PatchUpdate(
        nfkey=nfkey,
        courier_id=courier_id,
        status=None
    )
    db.add(novo_patch)
    db.commit()
    db.refresh(novo_patch)

    return {"message": "Patch registrado com sucesso. Envio será feito automaticamente.", "id": novo_patch.id}

@router.post("/patch/enviar-pendentes")
async def enviar_todos_patches_pendentes():
    try:
        await enviar_patches_pendentes()
        return {"message": "Envio de patches pendentes finalizado."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no envio de patches: {e}")
