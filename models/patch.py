from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from database import Base  # ou from app.database import Base

class PatchLog(Base):
    __tablename__ = "patch_logs"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(100), nullable=False)
    courier_id = Column(String(100), nullable=True)
    data_envio = Column(DateTime(timezone=True), default=func.now())  # nova coluna
    body_enviado = Column(JSON, nullable=False)  # nova coluna
    status_code = Column(Integer, nullable=True)  # nova coluna
    resposta = Column(JSON, nullable=True)  # nova coluna
