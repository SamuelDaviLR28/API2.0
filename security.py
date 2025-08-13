from fastapi import Header, HTTPException
import os

async def verificar_api_key(x_api_key: str = Header(default=None)):
    """
    Valida o header x-api-key contra a variável de ambiente API_KEY.
    """
    chave_correta = (os.getenv("API_KEY") or "").strip()

    if not chave_correta:
        raise HTTPException(status_code=500, detail="API_KEY não configurada no servidor.")

    enviada = (x_api_key or "").strip()
    if enviada != chave_correta:
        raise HTTPException(status_code=403, detail="API Key inválida")
