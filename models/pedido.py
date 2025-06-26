# models/pedido.py
from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base

class Pedido(Base):
    __tablename__ = "pedidos"  # nome da tabela no banco

    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String(100), index=True)
    data_criacao = Column(DateTime)
    json_completo = Column(Text)
