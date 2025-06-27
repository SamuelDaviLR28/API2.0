from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from database import Base

class Rastro(Base):
    __tablename__ = "rastros"

    id = Column(Integer, primary_key=True, index=True)
    nf_key = Column(String(44), nullable=False)
    courier_id = Column(Integer, nullable=False)
    eventos = Column(JSON, nullable=False)
    enviado = Column(Boolean, default=False)
    status_envio = Column(String(100), nullable=True)
    response_api = Column(JSON, nullable=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
