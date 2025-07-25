from sqlalchemy.orm import Session
from models import SLA

def buscar_sla(db: Session, uf_origem: str, uf_destino: str, cidade_destino: str | None = None) -> int | None:
    if cidade_destino:
        sla = db.query(SLA).filter(
            SLA.uf_origem == uf_origem.upper(),
            SLA.uf_destino == uf_destino.upper(),
            SLA.cidade_destino.ilike(cidade_destino)
        ).first()
        if sla:
            return sla.prazo_dias_uteis

    sla = db.query(SLA).filter(
        SLA.uf_origem == uf_origem.upper(),
        SLA.uf_destino == uf_destino.upper(),
        SLA.cidade_destino.is_(None)
    ).first()

    if sla:
        return sla.prazo_dias_uteis

    return None
