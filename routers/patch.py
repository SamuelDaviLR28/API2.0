from fastapi import APIRouter, HTTPException, Request, Query, Depends
import httpx
from sqlalchemy.orm import Session
from database import get_db
from models.patch import PatchLog
from datetime import datetime

router = APIRouter()

@router.patch("/patch")
async def enviar_patch_toutbox(
    request: Request,
    nfkey: str = Query(..., description="Chave da Nota Fiscal"),
    courier_id: str = Query(..., description="ID da transportadora"),
    db: Session = Depends(get_db),
):
    try:
        # ✅ Body JSON no formato RFC 6902
        patch_body = await request.json()  # Deve ser uma lista com op/replace, path e value

        url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={nfkey}&courier_id={courier_id}"

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=patch_body)

        try:
            resposta = response.json()
        except Exception:
            resposta = response.text

        # ✅ Salvar log no banco
        log = PatchLog(
            nfkey=nfkey,
            courier_id=courier_id,
            data_envio=datetime.utcnow(),
            body_enviado=patch_body,
            status_code=response.status_code,
            resposta=resposta
        )
        db.add(log)
        db.commit()

        return {
            "status": "Enviado para Toutbox",
            "status_code": response.status_code,
            "resposta": resposta
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar patch: {str(e)}")
