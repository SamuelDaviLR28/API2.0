from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base  # ajuste conforme sua estrutura de projeto

class Rastro(Base):
    __tablename__ = "rastros"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(50), nullable=False, index=True)
    payload = Column(JSON, nullable=False)  # body enviado
    status = Column(String(20))  # sucesso ou erro
    response = Column(Text)  # resposta da Toutbox (ou erro)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
