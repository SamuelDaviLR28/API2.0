from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from database import Base


class PatchLog(Base):
    __tablename__ = "patch_logs"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(100), nullable=False)
    courier_id = Column(String(100), nullable=True)
    patch_body = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
