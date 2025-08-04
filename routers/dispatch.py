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

@router.post("/dispatch", dependencies=[Depends(verificar_api_key)])
async def receber_dispatch(pedido: DispatchRequest, db: Session = Depends(get_db)):
    try:
        if not pedido.Itens or len(pedido.Itens) == 0:
            raise HTTPException(status_code=400, detail="Pedido sem itens.")

        # ✅ Função para serializar datetime
        def converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Tipo {type(obj)} não é serializável")

        # ✅ Serializa todo o pedido original (com suporte a datetime)
        json_serializado = json.dumps(pedido.model_dump(), indent=2, ensure_ascii=False, default=converter)

        # ✅ Usa o primeiro item para extrair chave e UFs
        item = pedido.Itens[0]

        # ✅ Extrai chave da nota fiscal
        chave_nfe = item.NotaFiscal.Chave if item.NotaFiscal else None
        if not chave_nfe:
            raise HTTPException(status_code=400, detail="Chave da NFe não encontrada no item.")

        # ✅ Extrai UFs
        uf_remetente = item.Frete.Remetente.Estado if item.Frete and item.Frete.Remetente else None
        uf_destinatario = item.Frete.Destinatario.Estado if item.Frete and item.Frete.Destinatario else None
        if not uf_remetente or not uf_destinatario:
            raise HTTPException(status_code=400, detail="UF de remetente ou destinatário ausente.")

        # ✅ Cria e salva o pedido no banco
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

        # ✅ Obtém courier_id
        courier_id = int(item.Frete.Transportadora.Id)

        # ✅ Cria PATCH pendente se ainda não existir
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
        print("❌ Erro ao processar pedido:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro interno ao salvar o pedido.")
