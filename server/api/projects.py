from fastapi import APIRouter, Depends, Body, Request, HTTPException, Query, Response
from core.utils.database import get_db
from core.handlers import ProjectHandler, SessionHandler
from pydantic import BaseModel, Field
from typing import Annotated, Dict, Optional, Any, List
from datetime import datetime
from core.utils.exceptions import InternalServerException, BadRequestException, NoniAPIException, centralized_error_handling
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/projects")

class ProjectModel(BaseModel):
    project_name: str = Field(max_length=50)
    description: str = Field(max_length=300)
    created_at: Annotated[datetime, Body()] = Field(None)
    modified_at: Annotated[datetime, Body()] = Field(None)

class FilterModel(BaseModel):
    filters: List[Dict[str, Any]] = []
    format: Optional[Dict[str, Any]] = {}

def get_project_handler(db=Depends(get_db)):
    return ProjectHandler(db)

async def check_request_session(request: Request, db=Depends(get_db)):
    session_handler = SessionHandler(db)
    return await session_handler.check_request_session(request)

@centralized_error_handling
@router.get("/all")
async def get_all_projects(
    handler: ProjectHandler = Depends(get_project_handler),
    valid_session: bool = Depends(check_request_session)
    ):
    results = handler._get_all()
    return results
    
@centralized_error_handling
@router.get("/{project_id}")
async def get_project_by_id(
    project_id: int,
    handler: ProjectHandler = Depends(get_project_handler),
    valid_session: bool = Depends(check_request_session)
    ):
    if not project_id:
        raise BadRequestException("No project_id found in request parameters")
    results = handler._filter_from(
        filters=[{
            "col": "project_id",
            "clause": "projects_equals",
            "value": project_id,
        }],
    )
    return results

@centralized_error_handling
@router.post("/")
async def filter_projects(
    filters: FilterModel,
    handler: ProjectHandler = Depends(get_project_handler),
    valid_session: bool = Depends(check_request_session)
    ):
    filter_data = filters.filters
    format_data = filters.format
    if not filter_data:
        raise BadRequestException("No filters found in request parameters")
    results = handler._filter_from(
        filters=filter_data,
        format=format_data
    )
    return results
    
@centralized_error_handling
@router.post("/")
async def create_project(
    response: Response,
    project_data: ProjectModel, 
    handler: ProjectHandler = Depends(get_project_handler)
    ):
    project_data = jsonable_encoder(project_data)
    session_id, project_id = handler.create_new_project(project_data)
    if session_id and project_id:
        response.set_cookie(
            key=SessionHandler.SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            max_age=SessionHandler.SESSION_EXPIRATION_SECONDS
        )
        return session_id,
    else:
        raise InternalServerException("Something went wrong while creating project.")

@centralized_error_handling
@router.post("/join/{session_id}")
async def join_project(
    response: Response,
    session_id: str,
    username: str,
    handler: ProjectHandler = Depends(get_project_handler)
    ):
    session_participant_id = handler.join_project(session_id, username)
    if session_participant_id:
        response.set_cookie(
            key=SessionHandler.SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            max_age=SessionHandler.SESSION_EXPIRATION_SECONDS
        )
        return session_participant_id
    else:
        raise InternalServerException("Something went wrong while joining project")

@centralized_error_handling
@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    handler: ProjectHandler = Depends(get_project_handler),
    valid_session: bool = Depends(check_request_session)
    ):
    """This does not currently work because of postgre constraint stuff"""
    delete_success = handler.delete_projects(
        project_id=project_id,
        session_id=valid_session
    )
    return "success" if delete_success else "error"