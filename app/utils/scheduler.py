from apscheduler.schedulers.background import BackgroundScheduler
from services.patch_sender import enviar_patches_pendentes
from services.rastro_sender import enviar_rastros_pendentes

scheduler = BackgroundScheduler()

# PATCH: Executa a cada 2 minutos
scheduler.add_job(enviar_patches_pendentes, 'interval', minutes=2)

# RASTRO: Executa a cada 3 minutos
scheduler.add_job(enviar_rastros_pendentes, 'interval', minutes=3)

def start():
    scheduler.start()
