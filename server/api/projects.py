from fastapi import APIRouter, Depends, Body, Request, HTTPException, Query, Response, Path, status
from core.utils.database import get_db
from core.handlers import ProjectHandler, SessionHandler
from pydantic import BaseModel, Field
from typing import Annotated, Dict, Optional, Any, List
from datetime import datetime
from core.utils.exceptions import InternalServerException, BadRequestException, NoniAPIException, centralized_error_handling
from fastapi.encoders import jsonable_encoder

##################################################
# API routes for project related functionalities #
##################################################

router = APIRouter(prefix="/projects", tags=["Projects"])

class ProjectModel(BaseModel):
    """Request schema for creating a new project"""
    project_name: str = Field(..., max_length=50, description="The name of the project. Must be under 50 characters.")
    description: Optional[str] = Field(None, max_length=300, description="A detailed description of the project. Max 300 characters.")
    created_at: Annotated[datetime, Body()] = Field(None, description="Optional creation timestamp. Defaults to now if not set.")
    modified_at: Annotated[datetime, Body()] = Field(None, description="Optional last modification timestamp.")

class FilterModel(BaseModel):
    """Schema used to define custom filters and output format options when querying projects"""
    filters: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="A list of filter dictionaries. Each should contain 'col', 'clause', and 'value'."
    )
    format: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional format settings (e.g., sorting, limit, fields)."
    )

def get_project_handler(db=Depends(get_db)):
    """Get correct handler for project related processes"""
    return ProjectHandler(db)

async def check_request_session(request: Request, db=Depends(get_db)):
    """
    Validates the request's session using a session cookie.
    Returns True if session is valid.
    """
    session_handler = SessionHandler(db)
    return await session_handler.check_request_session(request)

@centralized_error_handling
@router.get("/all", summary="Fetch all projects", response_description="List of all available projects")
async def get_all_projects(
    handler: ProjectHandler = Depends(get_project_handler),
    valid_session: bool = Depends(check_request_session)
):
    """
    Retrieve a list of all projects available in the database.
    
    - **Returns:** List of all project records.
    - **Requires:** A valid session cookie.
    """
    return handler._get_all()

@centralized_error_handling
@router.get("/{project_id}", summary="Get project by ID", response_description="Project details")
async def get_project_by_id(
    project_id: int = Path(..., description="The project ID to get data with"),
    handler: ProjectHandler = Depends(get_project_handler),
    valid_session: bool = Depends(check_request_session)
):
    """
    Get detailed information about a single project by its unique ID.

    - **project_id**: Integer ID of the project.
    - **Returns**: Matching project record, or raises 404 if not found.
    - **Requires**: A valid session cookie.
    """
    if not project_id:
        raise BadRequestException("No project_id found in request parameters")
    return handler._filter_from(filters=[{
        "col": "project_id",
        "clause": "projects_equals",
        "value": project_id,
    }])

@centralized_error_handling
@router.post("/filter", summary="Filter projects", response_description="Filtered project results")
async def filter_projects(
    filters: FilterModel,
    handler: ProjectHandler = Depends(get_project_handler),
    valid_session: bool = Depends(check_request_session)
):
    """
    Query projects using custom filters.

    - **filters**: A list of filtering conditions to apply.
    - **format**: Optional formatting options (e.g. pagination, sorting).
    - **Returns**: Projects that match the filter criteria.
    - **Requires**: A valid session.
    """
    if not filters.filters:
        raise BadRequestException("No filters found in request parameters")
    return handler._filter_from(filters=filters.filters, format=filters.format)

@centralized_error_handling
@router.post("/", summary="Create a new project", response_description="Session ID for the created project",
status_code=status.HTTP_201_CREATED)
async def create_project(
    response: Response,
    project_data: ProjectModel,
    handler: ProjectHandler = Depends(get_project_handler)
):
    """
    Create a new project and generate a session for the creator.

    - **project_data**: JSON body containing project_name and description.
    - **Returns**: Session ID if creation is successful.
    - **Sets Cookie**: Stores session ID in an HTTP-only cookie.
    """
    project_data = jsonable_encoder(project_data)
    session_id, project_id = handler.create_new_project(project_data)
    if session_id and project_id:
        response.set_cookie(
            key=SessionHandler.SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            max_age=SessionHandler.SESSION_EXPIRATION_SECONDS
        )
        return session_id
    raise InternalServerException("Something went wrong while creating project.")

@centralized_error_handling
@router.post("/join/{session_id}", summary="Join an existing project session", response_description="Session participant ID")
async def join_project(
    response: Response,
    session_id: str = Path(..., description="The session ID to join"),
    username: str = Query(..., description="Username of the participant"),
    handler: ProjectHandler = Depends(get_project_handler)
):
    """
    Join an existing collaborative session using the provided session ID.

    - **session_id**: The session token identifying the project.
    - **username**: The participant's display name.
    - **Returns**: A unique participant ID if successful.
    - **Sets Cookie**: Session ID cookie.
    """
    session_participant_id = handler.join_project(session_id, username)
    if session_participant_id:
        response.set_cookie(
            key=SessionHandler.SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            max_age=SessionHandler.SESSION_EXPIRATION_SECONDS
        )
        return session_participant_id
    raise InternalServerException("Something went wrong while joining project")

@centralized_error_handling
@router.delete("/{project_id}", summary="Delete a project", response_description="Success or error status")
async def delete_project(
    project_id: int = Path(..., description="The project ID to delete"),
    handler: ProjectHandler = Depends(get_project_handler),
    valid_session: bool = Depends(check_request_session)
):
    """
    Delete a project using its ID. 

    **Note:** This operation may fail if the project is linked to other resources due to foreign key constraints.

    - **project_id**: ID of the project to delete.
    - **Returns**: `"success"` if deletion succeeded, `"error"` otherwise.
    """
    delete_success = handler.delete_projects(
        project_id=project_id,
        session_id=valid_session
    )
    return "success" if delete_success else "error"
