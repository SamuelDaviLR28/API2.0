from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.models import Rota      
from app.schemas.rota import RotaPayload

router = APIRouter(prefix="/hooks/vivo")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/rota", status_code=status.HTTP_201_CREATED)
def post_rota(payload: RotaPayload, db: Session = Depends(get_db)):
    novo = Rota(dados=payload.dict(exclude_none=True))
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {"message": "Rota recebida", "id": novo.id}
