from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.pedido import Pedido
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/pedido")
async def receber_pedido(request: Request, db: Session = Depends(get_db)):
    pedido_json = await request.json()

    nfkey = pedido_json.get("NotaFiscal", {}).get("Chave")
    itens = pedido_json.get("Itens", [])

    if itens:
        frete = itens[0].get("Frete", {})
        remetente = frete.get("Remetente", {})
        destinatario = frete.get("Destinatario", {})

        uf_remetente = remetente.get("Estado", "").upper()
        uf_destinatario = destinatario.get("Estado", "").upper()
    else:
        uf_remetente = ""
        uf_destinatario = ""

    if not nfkey or nfkey.strip() == "":
        raise HTTPException(status_code=400, detail="NFKey (NotaFiscal.Chave) não encontrada no JSON")

    novo_pedido = Pedido(
        json_completo=pedido_json,
        nfkey=nfkey,
        uf_remetente=uf_remetente,
        uf_destinatario=uf_destinatario,
        data_criacao=datetime.utcnow()
    )

    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    return {"message": "Pedido recebido e salvo com sucesso", "id": novo_pedido.id}
