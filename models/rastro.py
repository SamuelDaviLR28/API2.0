from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base  # ou from database import Base se estiver fora da pasta `app`

class Rastro(Base):
    __tablename__ = "rastros"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(50), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    status = Column(String(20))
    response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
