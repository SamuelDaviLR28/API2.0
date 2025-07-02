from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import httpx
from datetime import datetime
from database import get_db
from models.patch import PatchLog  # modelo SQLAlchemy para tabela patch_logs

router = APIRouter()

class PatchRequest(BaseModel):
    nfkey: str
    sla: str  # ex: "1"
    courier_id: Optional[str] = None  # se vier, foi via dispatch; senão, manual

@router.patch("/patch")
async def enviar_patch(request: PatchRequest, db: Session = Depends(get_db)):
    if request.courier_id:
        # DISPATCH: usamos courier_id na URL e no body vai só o prazo
        url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={request.nfkey}&courier_id={request.courier_id}"
        body = [
            {
                "value": request.sla,
                "path": "/Itens/0/Frete/Transportadora/PrazoDiasUteis",
                "op": "replace"
            }
        ]
    else:
        # MANUAL: courier_id fica no body, não vai na URL
        url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={request.nfkey}"
        body = [
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

