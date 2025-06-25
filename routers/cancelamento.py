from fastapi import APIRouter

router = APIRouter()

@router.post("/cancelamento")
async def cancelar_entrega(payload: dict):
    print("Cancelamento solicitado:", payload)
    return {"status": "Cancelamento recebido"}

@router.post("/suspensao")
async def suspender_entrega(payload: dict):
    print("Suspensão solicitada:", payload)
    return {"status": "Suspensão recebida"}