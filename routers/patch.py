from fastapi import APIRouter, HTTPException, Query, Depends, Body
import httpx
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models.patch import PatchLog

router = APIRouter()

@router.patch("/patch")
async def enviar_patch_toutbox(
    payload: dict = Body(...),  # permite envio de JSON no body via Swagger/Postman
    nfkey: str = Query(..., description="Chave da Nota Fiscal"),
    courier_id: str = Query(None, description="ID da transportadora (para pedidos via dispatch)"),
    db: Session = Depends(get_db),
):
    try:
        # Montar URL da Toutbox
        url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={nfkey}"
        if courier_id:
            url += f"&courier_id={courier_id}"

        # Enviar PATCH para a Toutbox
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=payload)

        # Tentar extrair resposta como JSON, se possível
        try:
            resposta = response.json()
        except Exception:
            resposta = response.text

        # Registrar tentativa no banco
        log = PatchLog(
            nfkey=nfkey,
            courier_id=courier_id,
            data_envio=datetime.utcnow(),
            body_enviado=payload,
            status_code=response.status_code,
            resposta=resposta,
        )
        db.add(log)
        db.commit()

        # Retornar resultado da requisição externa
        return {
            "status": "Enviado para Toutbox",
            "status_code": response.status_code,
            "resposta": resposta
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar patch: {str(e)}")
