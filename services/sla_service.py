from sqlalchemy.orm import Session
from models.sla import SLA
from typing import Optional

def buscar_sla(db: Session, uf_origem: str, uf_destino: str, cidade_destino: Optional[str] = None) -> Optional[int]:
    query = db.query(SLA).filter(
        SLA.uf_origem == uf_origem,
        SLA.uf_destino == uf_destino
    )
    if cidade_destino:
        sla = query.filter(SLA.cidade_destino == cidade_destino).first()
        if sla:
            return sla.prazo
    sla = query.filter(SLA.cidade_destino == None).first()
    return sla.prazo if sla else None
