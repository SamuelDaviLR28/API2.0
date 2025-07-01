from fastapi import APIRouter, Request, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.patch import PatchLog
from datetime import datetime
import httpx

router = APIRouter()

@router.patch("/patch")
async def enviar_patch_toutbox(
    request: Request,
    nfkey: str = Query(..., description="Chave da Nota Fiscal"),
    courier_id: str = Query(..., description="ID da transportadora"),
    db: Session = Depends(get_db),
):
    try:
        patch_body = await request.json()  # Espera lista de operações, ex: [{"value":"1", "path":"/Itens/0/Frete/Transportadora/PrazoDiasUteis", "op":"replace"}]

        # Monta a URL com nfkey e courier_id
        url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={nfkey}&courier_id={courier_id}"

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=patch_body)

        try:
            resposta_json = response.json()
        except Exception:
            resposta_json = response.text

        # Salvar log no banco (se tiver o modelo e tabela)
        log = PatchLog(
            nfkey=nfkey,
            courier_id=courier_id,
            data_envio=datetime.utcnow(),
            body_enviado=patch_body,
            status_code=response.status_code,
            resposta=resposta_json,
        )
        db.add(log)
        db.commit()

        return {
            "status": "Enviado para Toutbox",
            "status_code": response.status_code,
            "resposta": resposta_json
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar patch: {str(e)}")
