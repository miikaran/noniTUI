from fastapi import APIRouter, Depends, Body, Request, HTTPException, Query
from core.utils.database import get_db
from pydantic import BaseModel, Field
from typing import Annotated, Dict, Optional, Any
from datetime import datetime
from core.handlers import MessageHandler
from core.utils.exceptions import InternalServerException, BadRequestException, centralized_error_handling
import json

##################################################
# API routes for message related functionalities #
##################################################

router = APIRouter(prefix="/messages", tags=["Messages"])

class MessageModel(BaseModel):
    project_id: int = Field()
    session_participant_id: int = Field()
    message_sender: str = Field(max_length=100)
    message_content: str = Field(max_length=500)
    message_timestamp: Annotated[datetime, Body()]

def get_message_handler(db=Depends(get_db)):
    return MessageHandler(db)

@centralized_error_handling
@router.get("/")
async def filter_messages(
    filters: str = Query(..., description="Filters messages as JSON String"),
    handler: MessageHandler = Depends(get_message_handler)
    ):
    filters_dict = json.loads(filters)
    if not filters_dict:
        raise BadRequestException("No filters found in request parameters")
    results = handler.filter_from(
        filters=filters_dict.get("filters", {}),
        format=filters_dict.get("format", {})
    )
    return {"results": results}

@centralized_error_handling
@router.post("/")
async def create_message(
    message_data: MessageModel, 
    handler: MessageHandler = Depends(get_message_handler)
    ):
    session_id = handler.create_message(message_data)
    if session_id:
        return {"session_id": session_id,}
