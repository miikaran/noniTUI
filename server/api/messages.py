from fastapi import APIRouter, Depends, Body, Request, HTTPException, Query
from core.utils.database import get_db
from pydantic import BaseModel, Field
from typing import Annotated, Dict, Optional, Any
from datetime import datetime
from core.handlers import MessageHandler, SessionHandler
from core.utils.exceptions import InternalServerException, BadRequestException, centralized_error_handling
from fastapi.encoders import jsonable_encoder

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

async def check_request_session(request: Request, db=Depends(get_db)):
    session_handler = SessionHandler(db)
    return await session_handler.check_request_session(request)

@centralized_error_handling
@router.get("/")
async def get_messages_by_project(
    handler: MessageHandler = Depends(get_message_handler),
    valid_session: bool = Depends(check_request_session)
):
    messages = handler.get_project_messages(valid_session)
    return messages

@centralized_error_handling
@router.post("/")
async def send_message_to_project(
    message_data: MessageModel,
    handler: MessageHandler = Depends(get_message_handler),
    valid_session: bool = Depends(check_request_session)
):
    data = jsonable_encoder(message_data)
    message_id = handler.send_project_message(data, valid_session)
    return message_id