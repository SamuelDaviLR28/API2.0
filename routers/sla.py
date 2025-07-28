from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.sla import SLA


router = APIRouter(prefix="/sla", tags=["SLA"])

@router.post("/")
def criar_sla(sla: SLACreate, db: Session = Depends(get_db)):
    existe = db.query(SLA).filter_by(
        uf_origem=sla.uf_origem.upper(),
        uf_destino=sla.uf_destino.upper(),
        cidade_destino=sla.cidade_destino
    ).first()

    if existe:
        raise HTTPException(status_code=400, detail="SLA já cadastrado.")

    novo_sla = SLA(
        uf_origem=sla.uf_origem.upper(),
        uf_destino=sla.uf_destino.upper(),
        cidade_destino=sla.cidade_destino,
        prazo_dias_uteis=sla.prazo_dias_uteis
    )

    db.add(novo_sla)
    db.commit()
    db.refresh(novo_sla)
    return novo_sla

@router.get("/", response_model=list[SLAResponse])
def listar_slas(db: Session = Depends(get_db)):
    return db.query(SLA).all()

@router.get("/buscar", response_model=SLAResponse)
def buscar_sla(uf_origem: str, uf_destino: str, cidade_destino: str | None = None, db: Session = Depends(get_db)):
    query = db.query(SLA).filter(
        SLA.uf_origem == uf_origem.upper(),
        SLA.uf_destino == uf_destino.upper()
    )

    if cidade_destino:
        query = query.filter(SLA.cidade_destino.ilike(cidade_destino.strip()))
    else:
        query = query.filter(SLA.cidade_destino.is_(None))

    sla = query.first()
    if not sla:
        raise HTTPException(status_code=404, detail="SLA não encontrado.")
    return sla
