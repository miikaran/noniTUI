from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Depends
from core.utils.exceptions import centralized_error_handling
from api.projects import check_request_session
from core.websocket_manager import WebsocketManager

##################################################
# Routes for websocket related functionalities   #
##################################################

router = APIRouter(prefix="/ws")

@centralized_error_handling
@router.websocket("/{participant_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    participant_id: int,
    websocket_manager: WebsocketManager = Depends(WebsocketManager),
    valid_session: bool = Depends(check_request_session)
):
    await websocket_manager.connect(websocket, valid_session, participant_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.send_personal_message(f"You wrote: {data}", websocket)
            await websocket_manager.broadcast(f"Client #{participant_id} says: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(valid_session, websocket)
        await websocket_manager.broadcast(f"Client #{participant_id} left the chat")
