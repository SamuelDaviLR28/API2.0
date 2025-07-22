from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from database import Base

class Rastro(Base):
    __tablename__ = "rastros"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(50), nullable=False, index=True)
    courier_id = Column(Integer, nullable=False)
    event_code = Column(String(10), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    address = Column(Text, nullable=True)
    number = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(10), nullable=True)
    receiver_document = Column(String(30), nullable=True)
    receiver = Column(String(100), nullable=True)
    geo_lat = Column(Float, nullable=True)
    geo_long = Column(Float, nullable=True)
    file_url = Column(Text, nullable=True)
    file_description = Column(Text, nullable=True)
    file_type = Column(String(20), nullable=True)
    enviado = Column(Integer, default=0)  # 0 = não enviado, 1 = enviado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
