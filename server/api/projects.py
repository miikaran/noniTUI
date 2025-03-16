from fastapi import APIRouter, Depends, Body, Request, HTTPException, Query
from core.database import get_db
from core.handlers import ProjectHandler
from pydantic import BaseModel, Field
from typing import Annotated, Dict, Optional, Any
from datetime import datetime
import json
from server.core.exceptions import InternalServerException, BadRequestException

router = APIRouter(prefix="/projects")

class ProjectModel(BaseModel):
    project_name: str = Field(max_length=50)
    description: str = Field(max_length=300)
    created_at: Annotated[datetime, Body()]
    modified_at: Annotated[datetime, Body()]

class FilterModel(BaseModel):
    filters: Dict[str, Any]
    format: Optional[Dict[str, Any]] = {}


def get_project_handler(db=Depends(get_db)):
    return ProjectHandler(db)

@router.get("/all")
async def get_all_projects(handler: ProjectHandler = Depends(get_project_handler)):
    try:
        results = handler.get_all()
        return {"results": results}
    except HTTPException: raise
    except Exception as e:
        raise InternalServerException


@router.get("/")
async def filter_projects(
    filters: str = Query(..., description="Filters as JSON String"),
    handler: ProjectHandler = Depends(get_project_handler)
):
    try:
        filters_dict = json.loads(filters)
        if not filters_dict:
            raise BadRequestException("No filters found in request parameters")
        results = handler.filter_from(
            filters=filters_dict.get("filters", {}),
            format=filters_dict.get("format", {})
        )
        return {"results": results}
    except HTTPException: raise
    except Exception as e:
        raise InternalServerException
    
@router.post("/")
async def create_project(project_data: dict, db=Depends(get_db)):
    return ProjectHandler(db).create_project({
        "project_name": "testiproject5",
        "description": "juu tälläne testi"
    })
