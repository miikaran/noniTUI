from fastapi import APIRouter, Depends
from core.database import get_db

router = APIRouter(prefix="/messages")
    
@router.get("/")
def get_messages(db=Depends(get_db)):
    return None

@router.post("/")
def create_task(message_data: dict, db=Depends(get_db)):
    return None
