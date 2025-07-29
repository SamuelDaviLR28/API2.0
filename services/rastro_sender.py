# routers/rastro.py

from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.rastro import Rastro
from datetime import datetime

router = APIRouter(prefix="/api/esl", tags=["Rastro ESL"])

@router.post("/eventos")
async def receber_evento_esl(
    request: Request,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Chave de API inválida")

    body = await request.json()

    evento = Rastro(
        nfkey=body["nfKey"],
        courier_id=body["courierId"],
        event_code=body["events"][0]["eventCode"],
        description=body["events"][0].get("description"),
        date=datetime.fromisoformat(body["events"][0]["date"]),
        address=body["events"][0]["address"],
        number=body["events"][0]["number"],
        city=body["events"][0]["city"],
        state=body["events"][0]["state"],
        receiver_document=body["events"][0].get("receiverDocument"),
        receiver=body["events"][0].get("receiver"),
        geo_lat=body["events"][0].get("geo", {}).get("lat"),
        geo_long=body["events"][0].get("geo", {}).get("long"),
        file_url=body["events"][0].get("files", [{}])[0].get("url"),
        file_description=body["events"][0].get("files", [{}])[0].get("description"),
        file_type=body["events"][0].get("files", [{}])[0].get("type"),
        payload=body,
        status="recebido",
        enviado=False,
    )

    db.add(evento)
    db.commit()

    return {"message": "Evento recebido com sucesso"}
