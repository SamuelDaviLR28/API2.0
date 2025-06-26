from fastapi import APIRouter

router = APIRouter()
@router.post('/cancelamento')
def cancelar(): return {'ok': True}