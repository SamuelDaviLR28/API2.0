from fastapi import APIRouter, HTTPException
from services.integracao import processar_nfkey
from database import SessionLocal
from models.patch import PatchUpdate

router = APIRouter()

@router.post("/integracao/processar/{nfkey}")
async def processar_nfkey_route(nfkey: str):
    try:
        await processar_nfkey(nfkey)
        return {"message": f"Processamento iniciado para nfkey {nfkey}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@router.post("/integracao/processar-todos")
async def processar_todos_patches():
    db = SessionLocal()
    try:
        patches = db.query(PatchUpdate).filter(PatchUpdate.status.is_(None)).all()
        for patch in patches:
            await processar_nfkey(patch.nfkey)
        return {"message": f"Processamento iniciado para {len(patches)} patches pendentes."}
    finally:
        db.close()
