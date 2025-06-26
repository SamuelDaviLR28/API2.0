from fastapi import APIRouter

router = APIRouter()
@router.post('/patch')
def patch(): return {'ok': True}