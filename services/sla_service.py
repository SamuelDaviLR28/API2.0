from sqlalchemy.orm import Session
from models.sla import SLA

def buscar_sla(db: Session, uf_origem: str, uf_destino: str, cidade_destino: str | None = None) -> int | None:
    if cidade_destino:
        sla = db.query(SLA).filter(
            SLA.uf_origem == uf_origem.upper(),
            SLA.uf_destino == uf_destino.upper(),
            SLA.cidade_destino.ilike(cidade_destino.strip())
        ).first()
        if sla:
            return sla.prazo_dias_uteis

    sla = db.query(SLA).filter(
        SLA.uf_origem == uf_origem.upper(),
        SLA.uf_destino == uf_destino.upper(),
        SLA.cidade_destino.is_(None)
    ).first()

    return sla.prazo_dias_uteis if sla else None
