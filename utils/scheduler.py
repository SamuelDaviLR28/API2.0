import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from services.patch_sender import enviar_patches_pendentes
from services.rastro_sender import enviar_rastros_pendentes
from services.esl_dispatch_sender import enviar_dispatch_para_esl
from database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

scheduler = None

def run_async(coro):
    """
    Roda uma coroutine async de forma segura,
    lidando com loop async já existente.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # já tem loop rodando: cria task para rodar async sem travar
        return asyncio.create_task(coro)
    else:
        # cria novo loop e roda a coroutine
        return asyncio.run(coro)

def enviar_dispatch_sync():
    try:
        enviar_dispatch_para_esl()
    except Exception as e:
        print("❌ Erro no envio de dispatch:", e)

def enviar_patches_sync():
    try:
        run_async(enviar_patches_pendentes())
    except Exception as e:
        print("❌ Erro no envio de patches:", e)

def enviar_rastros_sync():
    db = SessionLocal()
    try:
        run_async(enviar_rastros_pendentes(db))
    except Exception as e:
        print("❌ Erro no envio de rastros:", e)
    finally:
        db.close()

def start():
    global scheduler
    if scheduler and scheduler.running:
        print("Scheduler já rodando.")
        return

    scheduler = BackgroundScheduler(
        timezone="America/Sao_Paulo",
        executors={"default": ThreadPoolExecutor(max_workers=5)},
        job_defaults={"coalesce": False, "max_instances": 5},  # permite até 5 instâncias por job
    )

    scheduler.add_job(enviar_dispatch_sync, 'interval', minutes=5, id="dispatch_job")
    scheduler.add_job(enviar_patches_sync, 'interval', minutes=5, id="patch_job")
    scheduler.add_job(enviar_rastros_sync, 'interval', minutes=5, id="rastro_job")

    scheduler.start()
    print("⏰ Scheduler iniciado para Dispatch, Patch e Rastro a cada 5 minutos.")

def shutdown():
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        print("Scheduler parado.")
