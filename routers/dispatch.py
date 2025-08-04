from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.dispatch import DispatchRequest
from models.pedido import Pedido
from models.patch import PatchUpdate
from database import get_db
from security import verificar_api_key
import json
from datetime import datetime
import traceback

router = APIRouter()

@router.post("/", dependencies=[Depends(verificar_api_key)])
async def receber_dispatch(pedido: DispatchRequest, db: Session = Depends(get_db)):
    try:
        if not pedido.Itens or len(pedido.Itens) == 0:
            raise HTTPException(status_code=400, detail="Pedido sem itens.")

        def converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Tipo {type(obj)} não é serializável")

        json_serializado = json.dumps(pedido.model_dump(), indent=2, ensure_ascii=False, default=converter)

        item = pedido.Itens[0]

        if not item.NotaFiscal or not item.NotaFiscal.Chave:
            raise HTTPException(status_code=400, detail="Item sem chave de NFe válida.")

        chave_nfe = item.NotaFiscal.Chave

        if not item.Frete or not item.Frete.Remetente or not item.Frete.Destinatario:
            raise HTTPException(status_code=400, detail="Faltam dados de Frete, Remetente ou Destinatário.")

        uf_remetente = item.Frete.Remetente.Estado
        uf_destinatario = item.Frete.Destinatario.Estado

        if not uf_remetente or not uf_destinatario:
            raise HTTPException(status_code=400, detail="UF do remetente ou destinatário ausente.")

        pedido_existente = db.query(Pedido).filter_by(nfkey=chave_nfe).first()
        if pedido_existente:
            return {
                "status": "Pedido já existente",
                "id": pedido_existente.id
            }

        pedido_salvo = Pedido(
            nfkey=chave_nfe,
            numero_pedido=pedido.NumeroPedido,
            data_criacao=pedido.CriacaoPedido,
            uf_remetente=uf_remetente,
            uf_destinatario=uf_destinatario,
            json_completo=json_serializado
        )

        db.add(pedido_salvo)
        db.commit()
        db.refresh(pedido_salvo)

        # Valida courier_id
        if not item.Frete.Transportadora or not item.Frete.Transportadora.Id:
            raise HTTPException(status_code=400, detail="Transportadora ausente ou inválida.")

        courier_id = int(item.Frete.Transportadora.Id)

        patch_existente = db.query(PatchUpdate).filter_by(nfkey=chave_nfe, courier_id=courier_id).first()
        if not patch_existente:
            novo_patch = PatchUpdate(
                nfkey=chave_nfe,
                courier_id=courier_id
            )
            db.add(novo_patch)
            db.commit()

        return {"status": "Pedido salvo com sucesso", "id": pedido_salvo.id}

    except Exception as e:
        print(f"❌ Erro ao processar pedido {pedido.NumeroPedido}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro interno ao salvar o pedido.")
