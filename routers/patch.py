from fastapi import APIRouter, HTTPException, Query
import httpx

router = APIRouter()

@router.patch("/patch")
async def enviar_patch_toutbox(
    nfkey: str = Query(..., description="Chave da Nota Fiscal"),
    courier_id: str = Query(None, description="ID da transportadora (para pedidos via dispatch)"),
):
    try:
        url = f"http://production.toutbox.com.br/api/v1/external/api/v1/External/Order?nfkey={nfkey}"
        if courier_id:
            url += f"&courier_id={courier_id}"

        # Exemplo de corpo do PATCH
        patch_body = [
            {"value": "1", "path": "/Itens/0/Frete/Transportadora/PrazoDiasUteis", "op": "replace"},
            {"value": courier_id or "84", "path": "/Itens/0/Frete/Transportadora/id", "op": "replace"},
        ]

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=patch_body)

        return {
            "status_code": response.status_code,
            "response": response.json()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
