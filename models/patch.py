from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from database import Base  

class PatchLog(Base):
    __tablename__ = "patch_logs"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(100), nullable=False, index=True)
    courier_id = Column(String(100), nullable=True)
    data_envio = Column(DateTime(timezone=True), server_default=func.now())
    body_enviado = Column(JSON, nullable=False)
    status_code = Column(Integer, nullable=True)
    resposta = Column(JSON, nullable=True)
