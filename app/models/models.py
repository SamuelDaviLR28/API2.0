from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Dispatch(Base):
    __tablename__ = "dispatches"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), index=True)
    unique_id = Column(String(100), unique=True)
    client_info = Column(JSON)
    recipient_info = Column(JSON)
    invoice_info = Column(JSON)
    origin_info = Column(JSON)
    volumes = Column(JSON)


class Cancelamento(Base):
    __tablename__ = "cancelamentos"
    id = Column(Integer, primary_key=True, index=True)
    dados = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PatchFretePrazo(Base):
    __tablename__ = "patches"
    id = Column(Integer, primary_key=True, index=True)
    dados = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Rastro(Base):
    __tablename__ = "rastros"
    id = Column(Integer, primary_key=True, index=True)
    dados = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Motorista(Base):
    __tablename__ = "motoristas"
    id = Column(Integer, primary_key=True, index=True)
    dados = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Rota(Base):
    __tablename__ = "rotas"
    id = Column(Integer, primary_key=True, index=True)
    dados = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())