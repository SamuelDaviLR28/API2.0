from fastapi import APIRouter
from models.patch import PatchRequest

router = APIRouter()

@router.patch("/patch")
async def atualizar_patch(patch_data: PatchRequest):
    print("Patch recebido:", patch_data)
    return {"status": "Patch processado com sucesso"}