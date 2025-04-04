from fastapi import APIRouter, Depends, Body, Request, HTTPException, Query, Response
from core.utils.database import get_db
from core.handlers import TaskHandler, SessionHandler
from pydantic import BaseModel, Field
from typing import Annotated, Dict, Optional, Any, List
from datetime import datetime
from core.utils.exceptions import InternalServerException, BadRequestException, NoniAPIException, centralized_error_handling
from fastapi.encoders import jsonable_encoder
from api.projects import FilterModel

##################################################
# API routes for tasks related functionalities   #
##################################################

router = APIRouter(prefix="/tasks")

class TaskModel(BaseModel):
    project_id: int = Field(None)
    name: str = Field(max_length=255)
    assignee: str = Field(max_length=255)
    description: str = Field(max_length=300)
    start_date: Annotated[datetime, Body()] = Field(None)
    end_date: Annotated[datetime, Body()] = Field(None)
    task_type: str = Field(max_length=20, default="todo")
    end_date: Annotated[datetime, Body()] = Field(None)

def get_task_handler(db=Depends(get_db)):
    return TaskHandler(db)

async def check_request_session(request: Request, db=Depends(get_db)):
    session_handler = SessionHandler(db)
    return await session_handler.check_request_session(request)

@centralized_error_handling
@router.get("/all")
async def get_all_tasks(
    handler: TaskHandler = Depends(get_task_handler),
    valid_session: bool = Depends(check_request_session)
    ):
    results = handler._get_all()
    return results

@centralized_error_handling
@router.get("/{project_id}")
async def get_tasks_by_project(
    project_id: int,
    handler: TaskHandler = Depends(get_task_handler),
    valid_session: bool = Depends(check_request_session)
    ):
    project_tasks = handler.get_project_tasks(project_id)
    return project_tasks

@centralized_error_handling
@router.post("/")
async def filter_tasks(
    filters: FilterModel,
    handler: TaskHandler = Depends(get_task_handler),
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




    
