from apscheduler.schedulers.background import BackgroundScheduler
from services.patch_sender import enviar_patches_pendentes
from services.rastro_sender import enviar_rastros_pendentes

def start():
    scheduler = BackgroundScheduler()
    
    # Envia PATCHs automaticamente a cada 5 minutos
    scheduler.add_job(enviar_patches_pendentes, "interval", minutes=5)
    
    # Envia RASTROs automaticamente a cada 5 minutos
    scheduler.add_job(enviar_rastros_pendentes, "interval", minutes=5)
    
    scheduler.start()
