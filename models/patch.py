from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class PatchUpdate(Base):
    __tablename__ = "patch_updates"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(50), nullable=False, index=True)
    courier_id = Column(Integer, nullable=False)
    payload = Column(Text, nullable=True)
    status = Column(String(20), nullable=True)
    response = Column(Text, nullable=True)
    tentativas_envio = Column(Integer, default=0, nullable=False)  # <-- novo campo
    em_processo = Column(Boolean, default=False, nullable=False)   # opcional, se usar controle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
