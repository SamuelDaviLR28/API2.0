from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base

class RastroEvent(Base):
    __tablename__ = "rastros"

    id = Column(Integer, primary_key=True, index=True)
    nfkey = Column(String(50), nullable=False)
    courier_id = Column(Integer, nullable=False)
    event_code = Column(String(10), nullable=False)
    description = Column(Text)
    date = Column(DateTime(timezone=True))
    address = Column(Text)
    number = Column(String(20))
    city = Column(String(100))
    state = Column(String(10))
    receiver_document = Column(String(30))
    receiver = Column(String(100))
    geo_lat = Column(Float)
    geo_long = Column(Float)
    file_url = Column(Text)
    file_description = Column(Text)
    file_type = Column(String(20))
    enviado = Column(String(10), default="nao")  # sim ou nao
    created_at = Column(DateTime(timezone=True), server_default=func.now())
