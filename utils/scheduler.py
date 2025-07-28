import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from services.patch_sender import enviar_patches_pendentes
from services.rastro_sender import enviar_rastros_pendentes
from services.esl_dispatch_sender import enviar_dispatch_para_esl

# Wrappers síncronos para as funções async
def enviar_rastros_sync():
    asyncio.run(enviar_rastros_pendentes())

def enviar_patches_sync():
    asyncio.run(enviar_patches_pendentes())

def start():
    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    
    scheduler.add_job(enviar_dispatch_para_esl, 'interval', minutes=5, id="dispatch_job")
    scheduler.add_job(enviar_patches_sync, 'interval', minutes=5, id="patch_job")
    scheduler.add_job(enviar_rastros_sync, 'interval', minutes=5, id="rastro_job")
    
    scheduler.start()
    print("⏰ Scheduler iniciado para Dispatch, Patch e Rastro a cada 5 minutos.")
