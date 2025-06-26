from fastapi import APIRouter

router = APIRouter()

@router.patch("/patch")
def patch():
    return {"ok": True}
