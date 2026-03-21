from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/")
def root():
    return {"message": "Chào mừng đến với To-Do"}