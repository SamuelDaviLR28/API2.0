from fastapi import APIRouter
from models.rastro import RastroEvent

router = APIRouter()

@router.post("/rastro")
async def receber_rastro(eventos: RastroEvent):
    print("Eventos de rastreio:", eventos.json(indent=2, ensure_ascii=False))
    return {"status": "Eventos recebidos com sucesso"}