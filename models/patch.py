from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class PatchUpdate(Base):
    __tablename__ = "patch_updates"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(50), nullable=False, index=True)
    courier_id = Column(Integer, nullable=False)
    payload = Column(Text, nullable=True)  # pode ser JSON se estiver usando PostgreSQL
    status = Column(String(20), nullable=True)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
