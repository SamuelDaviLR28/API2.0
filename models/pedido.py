from sqlalchemy import Column, Integer, String, DateTime, JSON, Text

from sqlalchemy.sql import func
from database import Base

class Pedido(Base):
    __tablename__ = "pedidos"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String(100), nullable=False, index=True)
    cliente = Column(String(100), nullable=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String(20), default="pendente")  # pendente | enviado | erro
    response = Column(Text, nullable=True)
    json_completo = Column(JSON, nullable=True)
