from fastapi import FastAPI, Request, HTTPException
from routers import dispatch, patch, rastro, cancelamento
import os

app = FastAPI(title="API Integração Transportadora - Toutbox")

API_KEY = os.getenv("API_KEY")

@app.middleware("http")
async def autenticar_api_key(request: Request, call_next):
    if request.url.path.startswith(("/docs", "/openapi.json")):
        return await call_next(request)
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="API Key inválida")
    return await call_next(request)

app.include_router(dispatch.router)
app.include_router(patch.router)
app.include_router(rastro.router)
app.include_router(cancelamento.router)
