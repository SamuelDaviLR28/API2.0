from fastapi import FastAPI, Request, HTTPException
from fastapi.security.api_key import APIKeyHeader
from routers import dispatch, patch, rastro, cancelamento
import os

app = FastAPI(
    title="API Integração Transportadora - Toutbox",
    description="Insira sua chave no botão 'Authorize' para autenticar.",
    swagger_ui_parameters={"persistAuthorization": True}
)


api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

@app.middleware("http")
async def autenticar_api_key(request: Request, call_next):
    
    if request.url.path.startswith(("/docs", "/openapi.json", "/favicon.ico")):
        return await call_next(request)

   
    chave_enviada = request.headers.get("x-api-key")
    chave_configurada = os.getenv("API_KEY")

   
    print(f"🔐 Recebida: {chave_enviada} | Esperada: {chave_configurada}")

    
    if chave_enviada != chave_configurada:
        raise HTTPException(status_code=403, detail="API Key inválida")

    return await call_next(request)


app.include_router(dispatch.router)
app.include_router(patch.router)
app.include_router(rastro.router)
app.include_router(cancelamento.router)
