from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String, unique=True, index=True)
    data_criacao = Column(DateTime)
    json_completo = Column(Text)