from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from database import Base

class Pedido(Base):
    __tablename__ = "pedidos"
    __table_args__ = {"schema": "public"}  # força usar schema public

    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String(100), nullable=False)
    cliente = Column(String(100), nullable=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    json_completo = Column(JSON, nullable=True)
