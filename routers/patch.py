from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import SessionLocal  # Corrigido para importar da pasta app
from app.models.patch import PatchUpdate
import httpx
import os

router = APIRouter()

# Função para obter conexão com o banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota PATCH manual no formato JSON Patch (RFC 6902)
@router.patch("/patch")
async def enviar_patch_toutbox(
    request: Request,
    x_api_key: Optional[str] = Header(None)
):
    db: Session = next(get_db())

    # Tenta carregar o corpo como JSON Patch
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido.")

    # Obtém a chave nfkey da URL
    nfkey = request.query_params.get("nfkey")
    if not nfkey:
        raise HTTPException(status_code=400, detail="Parâmetro 'nfkey' é obrigatório.")

    # URL da API externa (Toutbox)
    url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={nfkey}&courier_id=84"

    # Envia PATCH
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=payload, timeout=10)

        status = "sucesso" if response.status_code < 300 else "erro"
        response_text = response.text

    except Exception as e:
        status = "erro"
        response_text = str(e)

    # Salva no banco de dados
    novo_patch = PatchUpdate(
        nfkey=nfkey,
        payload=payload,
        status=status,
        response=response_text
    )
    db.add(novo_patch)
    db.commit()

    # Retorna resposta
    return {
        "nfkey": nfkey,
        "status_envio": status,
        "resposta_toutbox": response_text
    }
