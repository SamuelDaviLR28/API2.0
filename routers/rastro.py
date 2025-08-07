from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.rastro import Rastro
from services.rastro_sender import enviar_rastros_pendentes
from security import verificar_api_key
import json
from datetime import datetime

router = APIRouter()

@router.post("/rastro", dependencies=[Depends(verificar_api_key)])
def receber_rastro(data: dict, db: Session = Depends(get_db)):
    try:
        events_data = data.get("eventsData", [])
        if not events_data:
            raise HTTPException(status_code=400, detail="Payload sem 'eventsData'")

        for evento_data in events_data:
            nfkey = evento_data.get("nfKey")
            courier_id = evento_data.get("CourierId")

            if not nfkey or not courier_id:
                raise HTTPException(status_code=400, detail="Campos obrigatórios faltando: 'nfKey' ou 'CourierId'")

            rastro = Rastro(
                nfkey=nfkey,
                payload=json.dumps({"eventsData": [evento_data]}),
                status="pendente",
                response=""
            )
            db.add(rastro)
        db.commit()

        return {"message": "Eventos recebidos com sucesso"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enviar-pendentes", dependencies=[Depends(verificar_api_key)])
def enviar_rastros(db: Session = Depends(get_db)):
    enviar_rastros_pendentes(db)
    return {"message": "Envio de rastros pendentes iniciado"}
