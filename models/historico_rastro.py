from sqlalchemy import Column, String, Text, DateTime, func
from app.database import Base

class HistoricoRastro(Base):
    __tablename__ = "historico_rastro"

    id = Column(String, primary_key=True, index=True)
    nfkey = Column(String, index=True)
    payload = Column(Text)
    status = Column(String)
    response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # <- ESSA LINHA
