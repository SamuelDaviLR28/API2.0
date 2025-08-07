from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database import Base

class HistoricoRastro(Base):
    __tablename__ = "historico_rastro"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(60), nullable=False)
    payload = Column(Text)
    status = Column(String(50))
    response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
