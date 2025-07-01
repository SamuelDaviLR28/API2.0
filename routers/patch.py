from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import httpx
from datetime import datetime
from database import get_db
from models.patch import PatchLog

router = APIRouter()

class PatchItem(BaseModel):
    nfkey: str
    courier_id: Optional[str] = None
    sla: str = "1"  # pode parametrizar o SLA se quiser

@router.post("/patch/batch")
async def enviar_patch_batch(
    items: List[PatchItem],
    db: Session = Depends(get_db),
):
    resultados = []
    async with httpx.AsyncClient() as client:
        for item in items:
            if item.courier_id:
                url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={item.nfkey}&courier_id={item.courier_id}"
                body = [
                    {
                        "value": item.sla,
                        "path": "/Itens/0/Frete/Transportadora/PrazoDiasUteis",
                        "op": "replace"
                    }
                ]
            else:
                url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={item.nfkey}"
                body = [
                    {
                        "value": item.sla,
                        "path": "/Itens/0/Frete/Transportadora/PrazoDiasUteis",
                        "op": "replace"
                    },
                    {
                        "value": "84",
                        "path": "/Itens/0/Frete/Transportadora/id",
                        "op": "replace"
                    }
                ]

            try:
                response = await client.patch(url, json=body)

                try:
                    resposta = response.json()
                except Exception:
                    resposta = response.text

                # Salvar log no banco
                log = PatchLog(
                    nfkey=item.nfkey,
                    courier_id=item.courier_id,
                    data_envio=datetime.utcnow(),
                    body_enviado=body,
                    status_code=response.status_code,
                    resposta=resposta,
                )
                db.add(log)
                db.commit()

                resultados.append({
                    "nfkey": item.nfkey,
                    "courier_id": item.courier_id,
                    "status_code": response.status_code,
                    "resposta": resposta
                })

            except Exception as e:
                resultados.append({
                    "nfkey": item.nfkey,
                    "courier_id": item.courier_id,
                    "error": str(e)
                })

    return {"resultados": resultados}
