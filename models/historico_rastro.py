from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class HistoricoRastro(Base):
    __tablename__ = "historico_rastro"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(50), nullable=False, index=True)
    payload = Column(Text, nullable=True)
    status = Column(String(20), nullable=True)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
