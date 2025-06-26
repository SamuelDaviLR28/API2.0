from fastapi import APIRouter

router = APIRouter()
@router.post('/rastro')
def rastro(): return {'ok': True}