from fastapi import APIRouter, Depends
from core.database import get_db

router = APIRouter(prefix="/tasks")

@router.get("/")
def get_tasks(db=Depends(get_db)):
    return None

@router.post("/")
def create_task(task_data: dict, db=Depends(get_db)):
    return None
