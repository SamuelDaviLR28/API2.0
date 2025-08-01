from fastapi import APIRouter, Depends, HTTPException 
from sqlalchemy.orm import Session
from models.dispatch import DispatchRequest
from models.pedido import Pedido
from database import get_db
from security import verificar_api_key
import json
from datetime import datetime
import traceback

router = APIRouter()

@router.post("/", dependencies=[Depends(verificar_api_key)])  # Corrigido aqui
async def receber_dispatch(pedido: DispatchRequest, db: Session = Depends(get_db)):
    try:
        if not pedido.Itens:
            raise HTTPException(status_code=400, detail="Pedido sem itens.")

        def converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Tipo {type(obj)} não é serializável")

        json_serializado = json.dumps(pedido.model_dump(), indent=2, ensure_ascii=False, default=converter)

        # Pega a chave da NFe com segurança
        chave_nfe = None
        if hasattr(pedido, "NFeChave") and pedido.NFeChave:
            chave_nfe = pedido.NFeChave
        elif hasattr(pedido, "NotaFiscal") and pedido.NotaFiscal and hasattr(pedido.NotaFiscal, "Chave"):
            chave_nfe = pedido.NotaFiscal.Chave

        if not chave_nfe:
            raise HTTPException(status_code=400, detail="Chave da NFe não encontrada no pedido.")

        pedido_salvo = Pedido(
            nfkey=chave_nfe,
            numero_pedido=pedido.NumeroPedido,
            data_criacao=pedido.CriacaoPedido,
            uf_remetente=pedido.Remetente.UF if pedido.Remetente else None,
            uf_destinatario=pedido.Destinatario.UF if pedido.Destinatario else None,
            json_completo=json_serializado
        )

        db.add(pedido_salvo)
        db.commit()
        db.refresh(pedido_salvo)

        return {"status": "Pedido salvo com sucesso", "id": pedido_salvo.id}

    except Exception as e:
        print("❌ Erro ao processar pedido:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))