from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from models.sla import SLA

router = APIRouter(prefix="/sla", tags=["SLA"])

@router.post("/")
def criar_sla(uf_origem: str, uf_destino: str, prazo_dias_uteis: int, db: Session = Depends(get_db)):
    existe = db.query(SLA).filter_by(uf_origem=uf_origem, uf_destino=uf_destino).first()
    if existe:
        raise HTTPException(status_code=400, detail="SLA já cadastrado.")
    
    sla = SLA(uf_origem=uf_origem.upper(), uf_destino=uf_destino.upper(), prazo_dias_uteis=prazo_dias_uteis)
    db.add(sla)
    db.commit()
    db.refresh(sla)
    return sla

@router.get("/")
def listar_slas(db: Session = Depends(get_db)):
    return db.query(SLA).all()

@router.get("/buscar")
def buscar_sla(uf_origem: str, uf_destino: str, db: Session = Depends(get_db)):
    sla = db.query(SLA).filter_by(uf_origem=uf_origem.upper(), uf_destino=uf_destino.upper()).first()
    if not sla:
        raise HTTPException(status_code=404, detail="SLA não encontrado.")
    return sla
