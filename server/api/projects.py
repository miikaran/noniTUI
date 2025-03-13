from fastapi import APIRouter, Depends
from core.database import get_db
from core.models.projects_model import ProjectsModel
from core.handlers import ProjectHandler
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/projects")

@router.get("/")
def get_projects(db=Depends(get_db)):
    return ProjectHandler.filter_projects(db, [{
        "col": "project_id",
        "clause": "projects_equals",
        "value": 1
    }])

@router.post("/")
def create_project(project_data: dict, db=Depends(get_db)):
    return ProjectHandler(db).create_project({
        "project_name": "testiproject5",
        "description": "juu tälläne testi"
    })
