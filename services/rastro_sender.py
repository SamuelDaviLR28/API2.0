import httpx
import os
import json
from dotenv import load_dotenv
from database import SessionLocal
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro

# Carrega variáveis do .env
load_dotenv()

TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")
if not TOUTBOX_API_KEY:
    raise Exception("Variável de ambiente TOUTBOX_API_KEY não definida!")

# Remove espaços em branco, caso existam
TOUTBOX_API_KEY = TOUTBOX_API_KEY.strip()

def validar_payload(payload: dict) -> tuple[bool, str]:
    try:
        evento_data = payload.get("eventsData", [{}])[0]

        if not evento_data.get("orderId"):
            return False, "Campo 'orderId' ausente."
        if not evento_data.get("CourierId"):
            return False, "Campo 'CourierId' ausente."
        eventos = evento_data.get("events", [])
        if not eventos:
            return False, "Lista 'events' vazia."

        evento = eventos[0]
        campos_obrigatorios = ["eventCode", "date", "city", "state", "address", "number"]
        for campo in campos_obrigatorios:
            if not evento.get(campo):
                return False, f"Campo obrigatório '{campo}' ausente no evento."

        return True, "válido"
    except Exception as e:
        return False, f"Erro ao validar payload: {str(e)}"

async def enviar_rastro_para_toutbox(payload: dict, courier_id: int):
    url = "http://courier.toutbox.com.br/api/v1/Parcel/Event"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOUTBOX_API_KEY}"
    }

    valido, msg_validacao = validar_payload(payload)
    nfkey = payload.get("eventsData", [{}])[0].get("orderId")

    if not valido:
        db = SessionLocal()
        try:
            historico = HistoricoRastro(
                nfkey=nfkey,
                payload=json.dumps(payload),
                status="erro - payload inválido",
                response=msg_validacao
            )
            db.add(historico)

            rastro = db.query(Rastro).filter(Rastro.nfkey == nfkey).first()
            if rastro:
                rastro.status = "erro - payload inválido"
                rastro.response = msg_validacao
                rastro.enviado = False

            db.commit()
        finally:
            db.close()

        return {
            "nfkey": nfkey,
            "status": "erro - payload inválido",
            "response": msg_validacao
        }

    print("🔍 Headers que serão enviados:", headers)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload, headers=headers)
    except Exception as e:
        return {
            "nfkey": nfkey,
            "status": "erro - exceção na requisição",
            "response": str(e)
        }

    status = "enviado" if response.status_code in [200, 204] else f"erro {response.status_code}"

    db = SessionLocal()
    try:
        historico = HistoricoRastro(
            nfkey=nfkey,
            payload=json.dumps(payload),
            status=status,
            response=response.text
        )
        db.add(historico)

        rastro = db.query(Rastro).filter(Rastro.nfkey == nfkey).first()
        if rastro:
            rastro.enviado = status == "enviado"
            rastro.status = status
            rastro.response = response.text

        db.commit()
    finally:
        db.close()

    return {
        "nfkey": nfkey,
        "status": status,
        "response": response.text
    }

def montar_payload_rastro(evento) -> dict:
    geo = None
    if evento.geo_lat and evento.geo_long:
        geo = {"lat": evento.geo_lat, "long": evento.geo_long}

    files = []
    if evento.file_url:
        files.append({
            "url": evento.file_url,
            "description": evento.file_description or "",
            "fileType": evento.file_type or "OUTRO"
        })

    return {
        "orderId": evento.nfkey,           # Corrigido para orderId, conforme payload correto
        "CourierId": evento.courier_id,
        "events": [{
            "eventCode": evento.event_code,
            "description": evento.description or "",
            "date": evento.date.isoformat() if evento.date else None,
            "address": evento.address,
            "number": evento.number,
            "city": evento.city,
            "state": evento.state,
            "receiverDocument": evento.receiver_document,
            "receiver": evento.receiver,
            "geo": geo,
            "files": files
        }]
    }

async def enviar_rastros_pendentes():
    db = SessionLocal()
    eventos = db.query(Rastro).filter(Rastro.enviado == False).all()

    for evento in eventos:
        item = montar_payload_rastro(evento)
        payload = {"eventsData": [item]}
        resultado = await enviar_rastro_para_toutbox(payload, evento.courier_id)

        evento.status = resultado["status"]
        evento.response = resultado["response"]
        evento.payload = json.dumps(payload)
        evento.enviado = resultado["status"] == "enviado"

    db.commit()
    db.close()
