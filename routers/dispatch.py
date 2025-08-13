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
        if not pedido.Itens:
            raise HTTPException(status_code=400, detail="Pedido sem itens.")

        item = pedido.Itens[0]

        # Nota fiscal pode ser None, mas se existir precisa de chave
        chave_nfe = pedido.NotaFiscal.Chave if pedido.NotaFiscal else None
        if chave_nfe is None:
            raise HTTPException(status_code=400, detail="Nota Fiscal ausente ou sem chave.")

        # Valida Frete mínimo
        if not item.Frete or not item.Frete.Remetente or not item.Frete.Destinatario:
            raise HTTPException(status_code=400, detail="Faltam dados de Frete, Remetente ou Destinatário.")

        uf_remetente = item.Frete.Remetente.Estado
        uf_destinatario = item.Frete.Destinatario.Estado

        for uf, nome in [(uf_remetente, "Remetente"), (uf_destinatario, "Destinatário")]:
            if not uf or len(uf.strip()) != 2:
                raise HTTPException(status_code=400, detail=f"UF do {nome} inválida: '{uf}'")

        # Evita duplicidade
        pedido_existente = db.query(Pedido).filter_by(nfkey=chave_nfe).first()
        if pedido_existente:
            return {"status": "Pedido já existente", "id": pedido_existente.id}

        # Serializa JSON completo
        def converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Tipo {type(obj)} não é serializável")

        json_serializado = json.dumps(pedido.model_dump(), indent=2, ensure_ascii=False, default=converter)

        pedido_salvo = Pedido(
            nfkey=chave_nfe,
            numero_pedido=pedido.NumeroPedido,
            data_criacao=pedido.CriacaoPedido,
            uf_remetente=uf_remetente.strip(),
            uf_destinatario=uf_destinatario.strip(),
            json_completo=json_serializado
        )

        db.add(pedido_salvo)
        db.commit()
        db.refresh(pedido_salvo)

        # Transportadora é opcional
        courier_id = int(item.Frete.Transportadora.Id) if item.Frete.Transportadora and item.Frete.Transportadora.Id else None
        if courier_id:
            patch_existente = db.query(PatchUpdate).filter_by(nfkey=chave_nfe, courier_id=courier_id).first()
            if not patch_existente:
                novo_patch = PatchUpdate(nfkey=chave_nfe, courier_id=courier_id)
                db.add(novo_patch)
                db.commit()

        return {"status": "Pedido salvo com sucesso", "id": pedido_salvo.id}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao processar pedido {pedido.NumeroPedido}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro interno ao salvar o pedido.")
