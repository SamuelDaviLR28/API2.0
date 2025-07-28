from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.sla import SLA
from pydantic import BaseModel

router = APIRouter()

class SLACreate(BaseModel):
    uf_origem: str
    uf_destino: str
    prazo_dias_uteis: int

@router.post("/")
def criar_sla(sla: SLACreate, db: Session = Depends(get_db)):
    novo_sla = SLA(
        uf_origem=sla.uf_origem,
        uf_destino=sla.uf_destino,
        prazo_dias_uteis=sla.prazo_dias_uteis
    )
    db.add(novo_sla)
    db.commit()
    db.refresh(novo_sla)
    return {"message": "SLA cadastrado com sucesso", "id": novo_sla.id}
