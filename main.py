from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import traceback

load_dotenv()

print("🔐 TOUTBOX_API_KEY carregada:", os.getenv("TOUTBOX_API_KEY"))
print("🔐 API_KEY carregada:", os.getenv("API_KEY"))

from routers import dispatch, patch, rastro, cancelamento, sla, integracao  # sem pedido

app = FastAPI(
    title="API Integração Transportadora - Toutbox",
    description="Insira sua chave no botão 'Authorize' para autenticar.",
    swagger_ui_parameters={"persistAuthorization": True}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def autenticar_api_key(request: Request, call_next):
    try:
        rotas_livres = ("/", "/docs", "/openapi.json", "/favicon.ico", "/redoc")

        if request.url.path in rotas_livres:
            return await call_next(request)

        rotas_sensiveis = ("/dispatch", "/patch", "/rastro", "/cancelamento", "/integracao")
        if any(request.url.path.startswith(r) for r in rotas_sensiveis):
            chave_enviada = request.headers.get("x-api-key")
            chave_configurada = os.getenv("API_KEY")

            print(f"🔑 Chave enviada no header x-api-key: {chave_enviada}")
            print(f"🔐 Chave configurada no ambiente API_KEY: {chave_configurada}")

            if not chave_configurada:
                raise HTTPException(status_code=500, detail="API_KEY não configurada no ambiente.")

            if (chave_enviada or "").strip() != chave_configurada.strip():
                raise HTTPException(status_code=403, detail="API Key inválida.")

        return await call_next(request)

    except Exception as e:
        print("🔥 Erro no middleware de autenticação:")
        traceback.print_exc()
        raise e

@app.on_event("startup")
def iniciar_agendador():
    print("🚀 Iniciando agendador de tarefas automáticas...")
    from utils.scheduler import start as start_scheduler
    start_scheduler()

@app.get("/")
def raiz():
    return {"mensagem": "API no ar com autenticação por API Key nas rotas sensíveis."}

app.include_router(dispatch, prefix="/dispatch", tags=["dispatch"])
app.include_router(patch, prefix="/patch", tags=["patch"])
app.include_router(rastro, prefix="/rastro", tags=["rastro"])
app.include_router(cancelamento, prefix="/cancelamento", tags=["cancelamento"])
app.include_router(sla, prefix="/sla", tags=["SLA"])
app.include_router(integracao, prefix="/integracao", tags=["integração"])
