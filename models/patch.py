from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from database import Base

class PatchLog(Base):
    __tablename__ = "patch_logs"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(100), nullable=False)
    courier_id = Column(String(100))
    data_envio = Column(DateTime(timezone=True), server_default=func.now())
    body_enviado = Column(JSON, nullable=False)
    status_code = Column(Integer)
    resposta = Column(JSON)
