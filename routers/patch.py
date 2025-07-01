from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import httpx
from datetime import datetime
from database import get_db
from models.patch import PatchLog

router = APIRouter()

class PatchRequest(BaseModel):
    nfkey: str
    courier_id: str
    sla: str  # ex: "1"

@router.patch("/patch")
async def enviar_patch(request: PatchRequest, db: Session = Depends(get_db)):
    url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={request.nfkey}&courier_id={request.courier_id}"

    body = [
        {
            "value": request.sla,
            "path": "/Itens/0/Frete/Transportadora/PrazoDiasUteis",
            "op": "replace"
        }
    ]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(url, json=body)

            # Tenta pegar resposta como JSON, se não der, pega como texto
            try:
                resposta = response.json()
            except Exception:
                resposta = response.text

            # Log da requisição no banco (mesmo se for erro)
            patch_log = PatchLog(
                nfkey=request.nfkey,
                courier_id=request.courier_id,
                data_envio=datetime.utcnow(),
                body_enviado=body,
                status_code=response.status_code,
                resposta=resposta
            )
            db.add(patch_log)
            db.commit()
            db.refresh(patch_log)

            # Verifica se foi sucesso
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail={
                    "erro": "Erro na Toutbox",
                    "resposta": resposta,
                    "status_code": response.status_code
                })

            return {
                "status": "Patch enviado com sucesso",
                "status_code": response.status_code,
                "resposta": resposta,
                "log_id": patch_log.id
            }

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
