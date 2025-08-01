import httpx
import os
import json
from dotenv import load_dotenv
from database import SessionLocal
from models.rastro import Rastro
from models.historico_rastro import HistoricoRastro

load_dotenv()

TOUTBOX_API_KEY = os.getenv("TOUTBOX_API_KEY")
if not TOUTBOX_API_KEY:
    raise Exception("Variável de ambiente TOUTBOX_API_KEY não definida!")
TOUTBOX_API_KEY = TOUTBOX_API_KEY.strip()


def validar_payload(payload: dict) -> tuple[bool, str]:
    try:
        evento_data = payload.get("eventsData", [{}])[0]

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
        "Authorization": TOUTBOX_API_KEY  # ✅ Header correto
    }

    nfkey = payload.get("eventsData", [{}])[0].get("nfKey")

    valido, msg_validacao = validar_payload(payload)
    if not valido:
        db = SessionLocal()
        try:
            historico = HistoricoRastro(
                nfkey=nfkey,
                payload=json.dumps(payload),
                status="erro - payload inválido",
                response=msg_validacao[:255]
            )
            db.add(historico)

            rastro = db.query(Rastro).filter(Rastro.nfkey == nfkey).first()
            if rastro:
                rastro.status = "erro - payload inválido"
                rastro.response = msg_validacao[:255]
                rastro.enviado = False

            db.commit()
        finally:
            db.close()

        return {
            "nfkey": nfkey,
            "status": "erro - payload inválido",
            "response": msg_validacao
        }

    print("🔐 Headers:", headers)
    print("📦 Payload:", json.dumps(payload, indent=2))

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload, headers=headers)
    except Exception as e:
        return {
            "nfkey": nfkey,
            "status": "erro - exceção na requisição",
            "response": str(e)[:255]
        }

    status = "enviado" if response.status_code in [200, 204] else f"erro {response.status_code}"

    db = SessionLocal()
    try:
        historico = HistoricoRastro(
            nfkey=nfkey,
            payload=json.dumps(payload),
            status=status,
            response=response.text[:255]
        )
        db.add(historico)

        rastro = db.query(Rastro).filter(Rastro.nfkey == nfkey).first()
        if rastro:
            rastro.enviado = status == "enviado"
            rastro.status = status
            rastro.response = response.text[:255]

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
    if evento.file_url and evento.file_url.strip():
        files.append({
            "url": evento.file_url.strip(),
            "description": evento.file_description or "",
            "fileType": (evento.file_type or "OUTRO").upper()
        })

    evento_dict = {
        "eventCode": evento.event_code,
        "description": evento.description or "",
        "date": evento.date.isoformat() if evento.date else None,
        "address": evento.address or "",
        "number": evento.number or "",
        "city": evento.city or "",
        "state": evento.state or "",
        "receiverDocument": evento.receiver_document,
        "receiver": evento.receiver,
        "geo": geo,
        "files": files
    }

    item = {
        "CourierId": evento.courier_id,
        "events": [evento_dict],
        "nfKey": evento.nfkey
        # ❌ Não enviar "orderId"
    }

    return item


async def enviar_rastros_pendentes():
    db = SessionLocal()
    try:
        eventos = db.query(Rastro).filter(Rastro.enviado.is_(False)).all()

        for evento in eventos:
            item = montar_payload_rastro(evento)
            payload = {"eventsData": [item]}
            resultado = await enviar_rastro_para_toutbox(payload, evento.courier_id)

            evento.status = resultado["status"]
            evento.response = resultado["response"][:255]
            evento.payload = json.dumps(payload)
            evento.enviado = resultado["status"] == "enviado"

        db.commit()
    finally:
        db.close()
