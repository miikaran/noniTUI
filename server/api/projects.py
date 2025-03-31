from fastapi import APIRouter, Depends, Body, Request, HTTPException, Query
from server.core.utils.database import get_db
from core.handlers import ProjectHandler
from pydantic import BaseModel, Field
from typing import Annotated, Dict, Optional, Any
from datetime import datetime
import json
from server.core.utils.exceptions import InternalServerException, BadRequestException
from fastapi.encoders import jsonable_encoder
import traceback 


router = APIRouter(prefix="/projects")

class ProjectModel(BaseModel):
    project_name: str = Field(max_length=50)
    description: str = Field(max_length=300)
    created_at: Annotated[datetime, Body()] = Field(None)
    modified_at: Annotated[datetime, Body()] = Field(None)

class FilterModel(BaseModel):
    filters: Dict[str, Any]
    format: Optional[Dict[str, Any]] = {}
    
def get_project_handler(db=Depends(get_db)):
    return ProjectHandler(db)

@router.get("/all")
async def get_all_projects(handler: ProjectHandler = Depends(get_project_handler)):
    try:
        results = handler._get_all()
        return {"results": results}
    except HTTPException: raise
    except Exception as e:
        print(e)
        raise InternalServerException
    
@router.get("/{project_id}")
async def get_project_by_id(
    project_id: int,
    handler: ProjectHandler = Depends(get_project_handler)
    ):
    try:
        if not project_id:
            raise BadRequestException("No project_id found in request parameters")
        results = handler._filter_from(
            filters=[{
                "col": "project_id",
                "clause": "projects_equals",
                "value": project_id,
            }],
        )
        return {"results": results}
    except HTTPException: raise
    except Exception as e:
        traceback.print_exc()
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
        results = handler._filter_from(
            filters=filters_dict.get("filters", {}),
            format=filters_dict.get("format", {})
        )
        return {"results": results}
    except HTTPException: raise
    except Exception as e:
        traceback.print_exc()
        raise InternalServerException
    
@router.post("/")
async def create_project(
    project_data: ProjectModel, 
    handler: ProjectHandler = Depends(get_project_handler)
    ):
    try:
        project_data = jsonable_encoder(project_data)
        session_id, project_id = handler.create_new_project(project_data)
        if session_id and project_id:
            return {
                "session_id": session_id,
                "project_id": project_id
            }
    except HTTPException: raise
    except Exception as e:
        traceback.print_exc()
        raise InternalServerException
    
@router.post("/join/{session_id}")
async def join_project(
    session_id: str,
    username: str,
    handler: ProjectHandler = Depends(get_project_handler)
    ):
    try:
        session_participant_id = handler.join_project(session_id, username)
        if session_participant_id:
            return {"session_participant_id": session_participant_id}
    except HTTPException: raise
    except Exception as e:
        traceback.print_exc() 
        raise InternalServerException
