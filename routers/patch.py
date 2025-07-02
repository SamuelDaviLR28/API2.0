from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import httpx
from datetime import datetime
from database import get_db
from models.patch import PatchLog

router = APIRouter()

class PatchRequest(BaseModel):
    nfkey: str
    sla: str  # ex: "1"

@router.patch("/patch")
async def enviar_patch(request: PatchRequest, db: Session = Depends(get_db)):
    # URL sem courier_id porque o pedido foi enviado via XML/Planilha
    url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={request.nfkey}"

    body = [
        {
            "value": "0",
            "path": "/Itens/0/Frete/Transportadora/ValorFrete",
            "op": "replace"
        },
        {
            "value": request.sla,
            "path": "/Itens/0/Frete/Transportadora/PrazoDiasUteis",
            "op": "replace"
        },
        {
            "value": "84",
            "path": "/Itens/0/Frete/Transportadora/id",
            "op": "replace"
        }
    ]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(url, json=body)

            try:
                resposta = response.json()
            except Exception:
                resposta = response.text

            # Log no banco de dados
            patch_log = PatchLog(
                nfkey=request.nfkey,
                courier_id="84",  # fixo porque foi manual
                data_envio=datetime.utcnow(),
                body_enviado=body,
                status_code=response.status_code,
                resposta=resposta
            )
            db.add(patch_log)
            db.commit()
            db.refresh(patch_log)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail={
                    "erro": "Erro na Toutbox",
                    "resposta": resposta,
                    "status_code": response.status_code
                })

            return {
                "status": "Patch enviado com sucesso",
                "resposta": resposta,
                "log_id": patch_log.id
            }

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
