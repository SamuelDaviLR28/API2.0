from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from database import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(50), nullable=False, unique=True, index=True)
    numero_pedido = Column(String(100), nullable=False)
    cliente = Column(String(100), nullable=True)  # ← existe no banco, adicione também
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String(50), default="pendente")
    response = Column(Text, nullable=True)
    uf_remetente = Column(String(2), nullable=True)
    uf_destinatario = Column(String(2), nullable=True)
    json_completo = Column(JSON, nullable=True)
