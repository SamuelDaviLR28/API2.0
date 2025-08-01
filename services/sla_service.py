from sqlalchemy.orm import Session
from models.sla import SLA
from typing import Optional

def buscar_sla(
    db: Session,
    uf_origem: str,
    uf_destino: str,
    cidade_destino: Optional[str] = None
) -> Optional[int]:
    """
    Busca o prazo SLA (em dias úteis) para o trajeto uf_origem -> uf_destino.
    Se cidade_destino for informada, tenta buscar SLA específico para cidade,
    caso contrário retorna SLA geral (com cidade_destino == None).

    :param db: Sessão do banco de dados
    :param uf_origem: UF de origem (ex: 'SP')
    :param uf_destino: UF de destino (ex: 'RJ')
    :param cidade_destino: (Opcional) Nome da cidade de destino para busca mais específica
    :return: Prazo em dias úteis se encontrado, senão None
    """

    query = db.query(SLA).filter(
        SLA.uf_origem == uf_origem,
        SLA.uf_destino == uf_destino
    )

    # Busca primeiro pelo SLA específico da cidade, se informado
    if cidade_destino:
        sla_cidade = query.filter(SLA.cidade_destino == cidade_destino).first()
        if sla_cidade:
            return sla_cidade.prazo

    # Se não encontrou SLA específico para cidade, busca SLA geral (cidade_destino == None)
    sla_geral = query.filter(SLA.cidade_destino == None).first()
    return sla_geral.prazo if sla_geral else None
