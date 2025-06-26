from fastapi import Header, HTTPException
import os

async def verificar_api_key(x_api_key: str = Header(default=None)):
    chave_correta = os.getenv("API_KEY")
    if not chave_correta:
        raise HTTPException(status_code=500, detail="API_KEY não configurada no servidor.")
    if x_api_key != chave_correta:
        raise HTTPException(status_code=403, detail="API Key inválida")