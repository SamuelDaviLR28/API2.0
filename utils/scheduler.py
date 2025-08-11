import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from services.patch_sender import enviar_patches_pendentes
from services.rastro_sender import enviar_rastros_pendentes_em_lotes
from services.esl_dispatch_sender import enviar_dispatch_para_esl
from database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

def enviar_dispatch_sync():
    try:
        enviar_dispatch_para_esl()
    except Exception as e:
        print("❌ Erro no envio de dispatch:", e)

def enviar_patches_sync():
    try:
        asyncio.run(enviar_patches_pendentes())
    except Exception as e:
        print("❌ Erro no envio de patches:", e)

def enviar_rastros_sync():
    db = SessionLocal()
    try:
        asyncio.run(enviar_rastros_pendentes_em_lotes(db))
    except Exception as e:
        print("❌ Erro no envio de rastros:", e)
    finally:
        db.close()

def start():
    scheduler = BackgroundScheduler(
        timezone="America/Sao_Paulo",
        executors={
            "default": ThreadPoolExecutor(max_workers=5)
        },
        job_defaults={
            "coalesce": False,
            "max_instances": 2
        }
    )

    scheduler.add_job(enviar_dispatch_sync, 'interval', minutes=5, id="dispatch_job")
    scheduler.add_job(enviar_patches_sync, 'interval', minutes=5, id="patch_job")
    scheduler.add_job(enviar_rastros_sync, 'interval', minutes=5, id="rastro_job")

    scheduler.start()
    print("⏰ Scheduler iniciado para Dispatch, Patch e Rastro a cada 5 minutos.")
