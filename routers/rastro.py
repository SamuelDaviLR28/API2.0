from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/rastro")
async def receber_evento_rastro(
    request: Request,
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(None)
):
    API_KEY = os.getenv("API_KEY")
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Chave de API inválida.")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido.")

    events_data = payload.get("eventsData")
    if not events_data or not isinstance(events_data, list):
        raise HTTPException(status_code=400, detail="Payload deve conter 'eventsData' como lista.")

    for event in events_data:
        # Remove orderId e trackingNumber se existirem
        event.pop("orderId", None)
        event.pop("trackingNumber", None)

        rastro = Rastro(
            nfkey=event.get("nfKey"),
            courier_id=event.get("CourierId"),
            event_code=(event.get("events") or [{}])[0].get("eventCode"),
            description=(event.get("events") or [{}])[0].get("description"),
            date=(event.get("events") or [{}])[0].get("date"),
            address=(event.get("events") or [{}])[0].get("address"),
            number=(event.get("events") or [{}])[0].get("number"),
            city=(event.get("events") or [{}])[0].get("city"),
            state=(event.get("events") or [{}])[0].get("state"),
            receiver_document=(event.get("events") or [{}])[0].get("receiverDocument"),
            receiver=(event.get("events") or [{}])[0].get("receiver"),
            geo_lat=(event.get("events") or [{}])[0].get("geo", {}).get("lat"),
            geo_long=(event.get("events") or [{}])[0].get("geo", {}).get("long"),
            file_url=((event.get("events") or [{}])[0].get("files") or [{}])[0].get("url"),
            file_description=((event.get("events") or [{}])[0].get("files") or [{}])[0].get("description"),
            file_type=((event.get("events") or [{}])[0].get("files") or [{}])[0].get("fileType"),
            status=None,
            response=None,
            enviado=False,
            payload=json.dumps(event)  # grava sem orderId e trackingNumber
        )
        db.add(rastro)

    db.commit()
    return {"message": "Eventos recebidos e salvos."}

@router.post("/rastro/enviar-pendentes")
async def enviar_todos_rastros_pendentes():
    try:
        await enviar_rastros_pendentes()
        return {"message": "Envio de rastros pendentes finalizado."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no envio de rastros: {e}")

# Alias para ESL (se desejar)
@router.post("/docs/api/esl/eventos")
async def alias_esl_eventos(request: Request, db: Session = Depends(get_db), x_api_key: Optional[str] = Header(None)):
    return await receber_evento_rastro(request, db, x_api_key)
