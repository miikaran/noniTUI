from fastapi import APIRouter, Depends, Body, Request, HTTPException, Query
from core.database import get_db
from pydantic import BaseModel, Field
from typing import Annotated, Dict, Optional, Any
from datetime import datetime
from core.handlers import MessageHandler
from server.core.exceptions import InternalServerException, BadRequestException
import json

router = APIRouter(prefix="/messages")

class MessageModel(BaseModel):
    project_id: int = Field()
    session_participant_id: int = Field()
    message_sender: str = Field(max_length=100)
    message_content: str = Field(max_length=500)
    message_timestamp: Annotated[datetime, Body()]

def get_message_handler(db=Depends(get_db)):
    return MessageHandler(db)

@router.get("/")
async def filter_messages(
    filters: str = Query(..., description="Filters messages as JSON String"),
    handler: MessageHandler = Depends(get_message_handler)
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
async def create_message(
    message_data: MessageHandler, 
    handler: MessageHandler = Depends(get_message_handler)
    ):
    try:
        session_id = handler.create_message(message_data)
        if session_id:
            return {"session_id": session_id,}
    except HTTPException: raise
    except Exception as e:
        raise InternalServerException
