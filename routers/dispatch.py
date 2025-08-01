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

@router.post("/dispatch", dependencies=[Depends(verificar_api_key)])
async def receber_dispatch(pedido: DispatchRequest, db: Session = Depends(get_db)):
    try:
        if not pedido.Itens:
            raise HTTPException(status_code=400, detail="Pedido sem itens.")

        # ✅ Função para converter datetime
        def converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Tipo {type(obj)} não é serializável")

        # ✅ Serializa com suporte a datetime
        json_serializado = json.dumps(pedido.model_dump(), indent=2, ensure_ascii=False, default=converter)

        print("✅ Pedido recebido:")
        print(json_serializado)

        # ✅ Monta e salva o pedido no banco com os campos necessários
        pedido_salvo = Pedido(
            nfkey=pedido.NFeChave,
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
