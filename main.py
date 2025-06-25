from fastapi import FastAPI, Request, HTTPException
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

API_KEY = os.getenv("API_KEY")

async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API Key inválida")
@app.get("/")
def raiz():
    return {"mensagem": "API no ar com autenticação por API Key."}

# Registrar rotas principais
app.include_router(dispatch.router)
app.include_router(patch.router)
app.include_router(rastro.router)
app.include_router(cancelamento.router)
