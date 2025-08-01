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
        # Lê CSV com separador ponto e vírgula (;)
        df = pd.read_csv(StringIO(content.decode('utf-8')), sep=';')
        
        # Normaliza nomes das colunas
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        
        # Validação das colunas obrigatórias
        colunas_esperadas = {'prazo', 'uf_origem', 'uf_destino'}
        faltando = colunas_esperadas - set(df.columns)
        if faltando:
            raise HTTPException(
                status_code=400,
                detail=f"Colunas obrigatórias faltando no CSV: {', '.join(faltando)}"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler CSV: {e}")

    db: Session = SessionLocal()
    try:
        for _, row in df.iterrows():
            uf_origem = row['uf_origem'].strip().upper()
            uf_destino = row['uf_destino'].strip().upper()
            cidade_destino = row.get('cidade_destino')
            if pd.isna(cidade_destino):
                cidade_destino = None
            else:
                cidade_destino = cidade_destino.strip()

            try:
                prazo = int(row['prazo'])
            except Exception:
                raise HTTPException(status_code=400, detail=f"Valor inválido para 'prazo' na linha {_ + 2}")

            # Verifica se SLA já existe para essa combinação
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
