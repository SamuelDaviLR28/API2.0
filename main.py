from fastapi import FastAPI, Request, HTTPException
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

# Importação das rotas
from routers import dispatch, patch, rastro, cancelamento

app = FastAPI(
    title="API Integração Transportadora - Toutbox",
    description="Insira sua chave no botão 'Authorize' para autenticar.",
    swagger_ui_parameters={"persistAuthorization": True}
)

# Middleware opcional (libera o acesso de outros domínios)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cabeçalho usado para autenticação via API Key
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

# Middleware para autenticar apenas rotas sensíveis
@app.middleware("http")
async def autenticar_api_key(request: Request, call_next):
    try:
        # Rotas públicas liberadas, sem autenticação
        if request.url.path.startswith(("/docs", "/openapi.json", "/favicon.ico", "/redoc", "/")):
            return await call_next(request)

        # Apenas protege rotas sensíveis
        rotas_sensiveis = ("/dispatch", "/patch", "/rastro", "/cancelamento")

        if any(request.url.path.startswith(r) for r in rotas_sensiveis):
            chave_enviada = request.headers.get("x-api-key")
            chave_configurada = os.getenv("API_KEY")

            print("🔍 Header recebido:", repr(chave_enviada))
            print("🔐 Variável API_KEY:", repr(chave_configurada))

            if not chave_configurada:
                raise HTTPException(status_code=500, detail="Variável de ambiente API_KEY não configurada.")

            if chave_enviada != chave_configurada:
                raise HTTPException(status_code=403, detail="API Key inválida")

        return await call_next(request)

    except Exception as e:
        print("🔥 Erro interno:", repr(e))
        raise HTTPException(status_code=500, detail="Erro interno ao processar o pedido.")

# Rota raiz para teste
@app.get("/")
def raiz():
    return {"mensagem": "API no ar com autenticação por API Key nas rotas sensíveis."}

# Registro das rotas
app.include_router(dispatch.router)
app.include_router(patch.router)
app.include_router(rastro.router)
app.include_router(cancelamento.router)
