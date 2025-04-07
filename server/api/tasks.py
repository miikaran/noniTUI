from fastapi import APIRouter, Depends, Body, Request, Path
from core.utils.database import get_db
from core.handlers import TaskHandler, SessionHandler
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime
from core.utils.exceptions import BadRequestException, centralized_error_handling
from fastapi.encoders import jsonable_encoder
from api.projects import FilterModel

##################################################
# API routes for tasks related functionalities   #
##################################################

router = APIRouter(prefix="/tasks", tags=["Tasks"])

class TaskModel(BaseModel):
    """
    Schema for creating and updating tasks.
    Represents a task that is associated with a project.
    """
    project_id: int = Field(..., description="ID of the project this task belongs to")
    name: str = Field(..., max_length=255, description="The name of the task")
    assignee: str = Field(..., max_length=255, description="The person assigned to the task")
    description: str = Field(..., max_length=300, description="Detailed description of the task")
    start_date: Annotated[datetime, Body()] = Field(None, description="The start date of the task")
    end_date: Annotated[datetime, Body()] = Field(None, description="The end date of the task")
    task_type: str = Field(default="todo", max_length=20, description="The type of the task (default is 'todo')")
    
def get_task_handler(db=Depends(get_db)):
    """
    Dependency to get the task handler for interacting with the database.
    """
    return TaskHandler(db)

async def check_request_session(request: Request, db=Depends(get_db)):
    """
    Validates the session of the incoming request.
    
    Returns `True` if the session is valid, otherwise raises an error.
    """
    session_handler = SessionHandler(db)
    return await session_handler.check_request_session(request)

@centralized_error_handling
@router.get("/all", summary="Fetch all tasks", response_description="List of all tasks")
async def get_all_tasks(
    handler: TaskHandler = Depends(get_task_handler),
    valid_session: bool = Depends(check_request_session)
):
    """
    Retrieve a list of all tasks across all projects.
    
    - **Returns**: A list of all tasks with details (ID, name, assignee, description, etc.).
    - **Requires**: A valid session token.
    """
    results = handler._get_all()
    return results

@centralized_error_handling
@router.get("/{project_id}", summary="Fetch tasks for a specific project", response_description="List of tasks for the given project")
async def get_tasks_by_project(
    project_id: int = Path(..., description="The project ID for which to fetch tasks"),
    handler: TaskHandler = Depends(get_task_handler),
    valid_session: bool = Depends(check_request_session)
):
    """
    Retrieve tasks associated with a specific project by its project ID.
    
    - **project_id**: Path parameter indicating the project to fetch tasks for.
    - **Returns**: A list of tasks associated with the specified project ID.
    - **Requires**: A valid session token.
    """
    project_tasks = handler.get_project_tasks(project_id)
    return project_tasks

@centralized_error_handling
@router.post("/", summary="Filter tasks by custom filters", response_description="Filtered list of tasks")
async def filter_tasks(
    filters: FilterModel,
    handler: TaskHandler = Depends(get_task_handler),
    valid_session: bool = Depends(check_request_session)
):
    """
    Filter tasks using custom filters (e.g., status, assignee, etc.) and formatting options (e.g., sorting).
    
    - **filters**: A JSON object containing filters and formatting options for the query.
    - **Returns**: A list of tasks that match the filter criteria.
    - **Requires**: A valid session token.
    """
    if not filters.filters:
        raise BadRequestException("No filters found in request parameters")
    results = handler._filter_from(filters=filters.filters, format=filters.format)
    return results

@centralized_error_handling
@router.post("/new", summary="Create a new task", response_description="ID of the newly created task")
async def add_task_to_project(
    task_data: TaskModel,
    handler: TaskHandler = Depends(get_task_handler),
    valid_session: bool = Depends(check_request_session)
):
    """
    Create a new task within an existing project.
    
    - **task_data**: JSON body containing the task's details (name, assignee, description, etc.).
    - **Returns**: The ID of the newly created task.
    - **Requires**: A valid session token.
    - **Sets Cookie**: The session ID will be stored in an HTTP-only cookie.
    """
    task_data = jsonable_encoder(task_data)
    task_id = handler.add_task_to_project(task_data, valid_session)
    return task_id

@centralized_error_handling
@router.put("/{task_id}", summary="Update an existing task", response_description="ID of the updated task")
async def update_project_task(
    task_id: int,
    task_data: TaskModel,
    handler: TaskHandler = Depends(get_task_handler),
    valid_session: bool = Depends(check_request_session)
):
    """
    Update an existing task's details in a project.
    
    - **task_data**: JSON body containing updated task information.
    - **Returns**: The ID of the updated task.
    - **Requires**: A valid session token.
    """
    task_data = jsonable_encoder(task_data)
    task_id = handler.update_project_task(task_data, task_id)
    return task_id

@centralized_error_handling
@router.delete("/{task_id}", summary="Delete a task", response_description="ID of the deleted task")
async def delete_task_from_project(
    task_id: int = Path(..., description="The ID of the task to delete"),
    handler: TaskHandler = Depends(get_task_handler),
    valid_session: bool = Depends(check_request_session)
):
    """
    Delete a specific task by its task ID.
    
    - **task_id**: Path parameter identifying the task to delete.
    - **Returns**: The ID of the deleted task if successful.
    - **Requires**: A valid session token.
    """
    task_id = handler.delete_task_from_project(
        task_id=task_id,
        session_id=valid_session
    )
    return task_id
