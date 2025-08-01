from fastapi import APIRouter, HTTPException
from services.integracao import processar_nfkey, processar_todos_patches_e_rastros

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
    try:
        await processar_todos_patches_e_rastros()
        return {"message": "Processamento de todos os patches pendentes finalizado."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento em massa: {str(e)}")
