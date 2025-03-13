from fastapi import APIRouter, Depends
from db.db import get_db
from models import messages_model

router = APIRouter(prefix="/messages")
    
@router.get("/")
def get_messages(db=Depends(get_db)):
    return None

@router.post("/")
def create_task(message_data: dict, db=Depends(get_db)):
    return None
