from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from database import Base

class Patch(Base):
    __tablename__ = "patches"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(50), nullable=False, index=True)  # Chave da nota
    courier_id = Column(Integer, nullable=False)  # Transportadora/Toutbox
    payload = Column(JSON, nullable=False)  # Conteúdo do PATCH
    status = Column(Integer, nullable=True)  # HTTP status do último envio
    response = Column(String, nullable=True)  # Texto da resposta da API
    enviado = Column(String(10), default="nao")  # Status de envio: 'sim' ou 'nao'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
