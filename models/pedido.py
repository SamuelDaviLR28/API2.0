from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from database import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(44), nullable=False, unique=True, index=True)  # chave NF-e
    uf_remetente = Column(String(2), nullable=False)
    uf_destinatario = Column(String(2), nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String(20), default="pendente")
    response = Column(Text, nullable=True)
    json_completo = Column(JSON, nullable=True)
