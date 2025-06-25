from fastapi import FastAPI, Request, HTTPException
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do .env
load_dotenv()

# Importação das rotas (certifique-se de que existem esses arquivos em routers/)
from routers import dispatch, patch, rastro, cancelamento

app = FastAPI(
    title="API Integração Transportadora - Toutbox",
    description="Insira sua chave no botão 'Authorize' para autenticar.",
    swagger_ui_parameters={"persistAuthorization": True}
)

# Header usado para autenticação via API Key
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

# Middleware para autenticar todas as rotas privadas
@app.middleware("http")
async def autenticar_api_key(request: Request, call_next):
    try:
        # Liberar acesso para documentação e arquivos públicos
        if request.url.path.startswith((
            "/docs", "/openapi.json", "/favicon.ico", "/redoc"
        )):
            return await call_next(request)

        # Obter chave do header e do .env
        chave_enviada = request.headers.get("x-api-key")
        chave_configurada = os.getenv("API_KEY")

        # Logs para depuração
        print("🔍 Header recebido:", repr(chave_enviada))
        print("🔐 Variável API_KEY:", repr(chave_configurada))

        if not chave_configurada:
            raise HTTPException(status_code=500, detail="Variável de ambiente API_KEY não configurada.")

        if chave_enviada != chave_configurada:
            raise HTTPException(status_code=403, detail="API Key inválida")

        # Se passou, segue para a rota
        return await call_next(request)

    except Exception as e:
        print("🔥 Erro interno:", repr(e))
        raise HTTPException(status_code=500, detail="Erro interno ao processar o pedido.")

# Rota simples para teste (opcional)
@app.get("/")
def raiz():
    return {"mensagem": "API no ar com autenticação por API Key."}

# Registrar rotas principais
app.include_router(dispatch.router)
app.include_router(patch.router)
app.include_router(rastro.router)
app.include_router(cancelamento.router)
