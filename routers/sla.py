from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO
from database import SessionLocal
from models.sla import SLA

router = APIRouter()

@router.post("/sla/importar-csv")
async def importar_sla_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")

    content = await file.read()

    try:
        # 🔧 CSV separado por ponto e vírgula
        df = pd.read_csv(StringIO(content.decode('utf-8')), sep=';')
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]  # normaliza colunas
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler CSV: {e}")

    db: Session = SessionLocal()
    try:
        for _, row in df.iterrows():
            uf_origem = row['uf_origem']
            uf_destino = row['uf_destino']
            cidade_destino = row.get('cidade_destino')
            prazo = int(row['prazo'])

            sla_existente = db.query(SLA).filter_by(
                uf_origem=uf_origem,
                uf_destino=uf_destino,
                cidade_destino=cidade_destino
            ).first()

            if sla_existente:
                sla_existente.prazo = prazo
            else:
                sla = SLA(
                    uf_origem=uf_origem,
                    uf_destino=uf_destino,
                    cidade_destino=cidade_destino,
                    prazo=prazo
                )
                db.add(sla)
        db.commit()
    finally:
        db.close()

    return {"message": "Importação concluída com sucesso"}
