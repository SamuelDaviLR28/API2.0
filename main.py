from fastapi import FastAPI, Request, HTTPException
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import sla
import os
import traceback

# Carrega variáveis do .env
load_dotenv()
print("🔑 API_KEY carregada:", os.getenv("API_KEY"))  # Remover após testes

# Importação das rotas
from routers import dispatch, patch, rastro, cancelamento,sla

# Importa o agendador automático
from utils.scheduler import start as start_scheduler

app = FastAPI(
    title="API Integração Transportadora - Toutbox",
    description="Insira sua chave no botão 'Authorize' para autenticar.",
    swagger_ui_parameters={"persistAuthorization": True}
)

# Libera todas as origens (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de autenticação para rotas sensíveis
@app.middleware("http")
async def autenticar_api_key(request: Request, call_next):
    try:
        rotas_livres = ("/", "/docs", "/openapi.json", "/favicon.ico", "/redoc")

        if request.url.path in rotas_livres:
            return await call_next(request)

        rotas_sensiveis = ("/dispatch", "/patch", "/rastro", "/cancelamento")
        if any(request.url.path.startswith(r) for r in rotas_sensiveis):
            chave_enviada = request.headers.get("x-api-key")
            chave_configurada = os.getenv("API_KEY")

            if not chave_configurada:
                raise HTTPException(status_code=500, detail="API_KEY não configurada no ambiente.")

            if chave_enviada != chave_configurada:
                raise HTTPException(status_code=403, detail="API Key inválida.")

        return await call_next(request)

    except Exception as e:
        print("🔥 Erro no middleware de autenticação:")
        traceback.print_exc()
        raise e

# Executa tarefas agendadas automaticamente no startup
@app.on_event("startup")
async def iniciar_agendador():
    print("🚀 Iniciando agendador de tarefas automáticas...")
    start_scheduler()

# Rota raiz
@app.get("/")
def raiz():
    return {"mensagem": "API no ar com autenticação por API Key nas rotas sensíveis."}

# Registro das rotas com prefixos
app.include_router(dispatch.router, prefix="/dispatch", tags=["dispatch"])
app.include_router(patch.router, prefix="/patch", tags=["patch"])
app.include_router(rastro.router, prefix="/rastro", tags=["rastro"])
app.include_router(cancelamento.router, prefix="/cancelamento", tags=["cancelamento"])
app.include_router(sla.router, prefix="/sla", tags=["SLA"])
