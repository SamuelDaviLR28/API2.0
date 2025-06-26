from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.dispatch import DispatchRequest
from models.pedido import Pedido
from database import get_db
from security import verificar_api_key

import traceback

router = APIRouter()

@router.post("/dispatch", dependencies=[Depends(verificar_api_key)])
async def receber_dispatch(pedido: DispatchRequest, db: Session = Depends(get_db)):
    try:
        if not pedido.Itens:
            raise HTTPException(status_code=400, detail="Pedido sem itens.")

        # Serializa todo o JSON recebido
        json_serializado = pedido.model_dump_json(indent=2, ensure_ascii=False)

        print("✅ Pedido recebido:")
        print(json_serializado)

        # Salva no banco
        pedido_salvo = Pedido(
            numero_pedido=pedido.NumeroPedido,
            data_criacao=pedido.CriacaoPedido,
            json_completo=json_serializado
        )

        db.add(pedido_salvo)
        db.commit()
        db.refresh(pedido_salvo)

        return {"status": "Pedido salvo com sucesso", "id": pedido_salvo.id}

    except Exception as e:
        print("❌ Erro ao processar pedido:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro interno ao processar o pedido.")
