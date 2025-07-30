from sqlalchemy import Column, Integer, String
from database import Base

class SLA(Base):
    __tablename__ = "sla"
    id = Column(Integer, primary_key=True)
    uf_origem = Column(String(2), nullable=False)
    uf_destino = Column(String(2), nullable=False)
    cidade_destino = Column(String, nullable=True)  # Essa coluna precisa existir no banco!
    prazo = Column(Integer, nullable=False)
