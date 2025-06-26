from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class PatchOperation(BaseModel):
    op: str
    path: str
    value: str  # ou Union[str, int, float] se quiser aceitar outros tipos

@router.patch("/patch")
def aplicar_patch(operations: List[PatchOperation]):
    try:
        # Exemplo de resposta simulando aplicação dos patches
        for op in operations:
            print(f"Aplicando operação: {op.op} no campo {op.path} com valor {op.value}")
        
        # Aqui você aplicaria as mudanças no banco ou objeto real
        return {"status": "Patches aplicados com sucesso", "detalhes": [op.dict() for op in operations]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao aplicar patch: {str(e)}")
