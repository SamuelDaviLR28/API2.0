from sqlalchemy import Column, Integer, String
from database import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String(100), nullable=False)
    cliente = Column(String(100), nullable=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
