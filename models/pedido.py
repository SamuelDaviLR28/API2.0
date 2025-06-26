from sqlalchemy import Column, Integer, String
from database import Base

class Pedido(Base):
    __tablename__ = "pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, nullable=False)
    status = Column(String, nullable=True)
