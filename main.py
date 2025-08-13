from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import traceback

# Carregar variáveis de ambiente
load_dotenv()

print("🔐 TOUTBOX_API_KEY carregada:", os.getenv("TOUTBOX_API_KEY"))
print("🔐 API_KEY carregada:", os.getenv("API_KEY"))

# Importar routers
from routers import dispatch, patch, rastro, cancelamento, sla, integracao

app = FastAPI(
    title="API Integração Transportadora - Toutbox",
    description="Insira sua chave no botão 'Authorize' para autenticar.",
    swagger_ui_parameters={"persistAuthorization": True}
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de autenticação
@app.middleware("http")
async def autenticar_api_key(request: Request, call_next):
    try:
        rotas_livres = ("/", "/docs", "/openapi.json", "/favicon.ico", "/redoc")
        if request.url.path in rotas_livres:
            return await call_next(request)

        rotas_sensiveis = ("/dispatch", "/patch", "/rastro", "/cancelamento", "/integracao")
        if any(request.url.path.startswith(r) for r in rotas_sensiveis):
            chave_enviada = (request.headers.get("x-api-key") or "").strip()
            chave_configurada = (os.getenv("API_KEY") or "").strip()

            print(f"🔑 Chave enviada no header: '{chave_enviada}'")
            print(f"🔐 Chave configurada no .env: '{chave_configurada}'")

            if not chave_configurada:
                raise HTTPException(status_code=500, detail="API_KEY não configurada no ambiente.")

            if chave_enviada != chave_configurada:
                print("❌ Chave inválida!")
                raise HTTPException(status_code=403, detail="API Key inválida.")

        return await call_next(request)

    except HTTPException:
        raise
    except Exception:
        print("🔥 Erro inesperado no middleware de autenticação:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro interno de autenticação.")

# Startup
@app.on_event("startup")
def iniciar_agendador():
    print("🚀 Iniciando agendador de tarefas automáticas...")
    from utils.scheduler import start as start_scheduler
    start_scheduler()

# Rota raiz
@app.get("/")
def raiz():
    return {"mensagem": "API no ar com autenticação por API Key nas rotas sensíveis."}

# Incluir routers
# Adicionando barra final para evitar redirecionamentos
app.include_router(dispatch, prefix="/dispatch/", tags=["dispatch"])
app.include_router(patch, prefix="/patch/", tags=["patch"])
app.include_router(rastro, prefix="/rastro/", tags=["rastro"])
app.include_router(cancelamento, prefix="/cancelamento/", tags=["cancelamento"])
app.include_router(sla, prefix="/sla/", tags=["SLA"])
app.include_router(integracao, prefix="/integracao/", tags=["integração"])
