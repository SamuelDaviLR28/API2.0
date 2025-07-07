from fastapi import FastAPI, Request, HTTPException
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

# Importação das rotas
from routers import dispatch, patch, rastro, cancelamento

# Importa o agendador
from utils.scheduler import start as start_scheduler

app = FastAPI(
    title="API Integração Transportadora - Toutbox",
    description="Insira sua chave no botão 'Authorize' para autenticar.",
    swagger_ui_parameters={"persistAuthorization": True}
)

# Libera CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cabeçalho da API Key
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

# Middleware para autenticação
@app.middleware("http")
async def autenticar_api_key(request: Request, call_next):
    try:
        # Rotas públicas
        rotas_livres = ("/", "/docs", "/openapi.json", "/favicon.ico", "/redoc")
        if request.url.path in rotas_livres:
            return await call_next(request)

        # Rotas sensíveis com proteção
        rotas_sensiveis = ("/dispatch", "/patch", "/rastro", "/cancelamento")
        if any(request.url.path.startswith(r) for r in rotas_sensiveis):
            chave_enviada = request.headers.get("x-api-key")
            chave_configurada = os.getenv("API_KEY")

            if not chave_configurada:
                raise HTTPException(status_code=500, detail="Variável de ambiente API_KEY não configurada.")

            if chave_enviada != chave_configurada:
                raise HTTPException(status_code=403, detail="API Key inválida")

        return await call_next(request)

    except Exception as e:
        print("🔥 Erro interno:", repr(e))
        raise HTTPException(status_code=500, detail="Erro interno ao processar o pedido.")

# Evento de inicialização para o agendador automático
@app.on_event("startup")
async def iniciar_agendador():
    print("🚀 Iniciando agendador de tarefas automáticas...")
    start_scheduler()

# Rota raiz
@app.get("/")
def raiz():
    return {"mensagem": "API no ar com autenticação por API Key nas rotas sensíveis."}

# Registro das rotas
app.include_router(dispatch.router)
app.include_router(patch.router)
app.include_router(rastro.router)
app.include_router(cancelamento.router)
