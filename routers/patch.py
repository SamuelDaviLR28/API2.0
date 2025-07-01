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
    courier_id: str = Query(None, description="ID da transportadora (para pedidos via dispatch)"),
    db: Session = Depends(get_db),
):
    try:
        patch_body = await request.json()

        url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={nfkey}"
        if courier_id:
            url += f"&courier_id={courier_id}"

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=patch_body)

        # Tenta decodificar o JSON, senão pega como texto
        try:
            resposta = response.json()
        except Exception:
            resposta = response.text

        # Salvar log da requisição/resposta
        log = PatchLog(
            nfkey=nfkey,
            courier_id=courier_id,
            data_envio=datetime.utcnow(),
            body_enviado=patch_body,
            status_code=response.status_code,
            resposta=resposta,
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
