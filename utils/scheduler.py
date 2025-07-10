from apscheduler.schedulers.background import BackgroundScheduler
from services.patch_sender import enviar_patches_pendentes
from services.rastro_sender import enviar_rastros_pendentes
from services.esl_dispatch_sender import enviar_dispatch_para_esl

def start():
    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    
    scheduler.add_job(enviar_dispatch_para_esl, 'interval', minutes=5, id="dispatch_job")
    scheduler.add_job(enviar_patches_pendentes, 'interval', minutes=5, id="patch_job")
    scheduler.add_job(enviar_rastros_pendentes, 'interval', minutes=5, id="rastro_job")
    
    scheduler.start()
    print("⏰ Scheduler iniciado para Dispatch, Patch e Rastro a cada 5 minutos.")
