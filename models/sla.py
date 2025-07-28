from sqlalchemy import Column, Integer, String
from database import Base

class SLA(Base):
    __tablename__ = "sla"
    id = Column(Integer, primary_key=True, index=True)
    uf_origem = Column(String(2), nullable=False, index=True)
    uf_destino = Column(String(2), nullable=False, index=True)
    cidade_destino = Column(String(100), nullable=True, index=True)
    prazo_dias_uteis = Column(Integer, nullable=False)
    cidade_destino = Column(String, nullable=True)
