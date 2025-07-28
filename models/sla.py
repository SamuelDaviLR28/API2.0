from sqlalchemy import Column, Integer, String
from app.database import Base

class SLA(Base):
    __tablename__ = "sla"

    id = Column(Integer, primary_key=True, index=True)
    uf_origem = Column(String, index=True, nullable=False)
    uf_destino = Column(String, index=True, nullable=False)
    cidade_destino = Column(String, index=True, nullable=True)
    prazo_dias_uteis = Column(Integer, nullable=False)
