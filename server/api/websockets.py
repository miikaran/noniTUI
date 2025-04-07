from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Depends
from core.utils.exceptions import centralized_error_handling
from core.websocket_manager import WebsocketManager

##################################################
# Routes for websocket related functionalities   #
##################################################

router = APIRouter(prefix="/ws")
websocket_manager = WebsocketManager()

@centralized_error_handling
@router.websocket("/{session_id}/{participant_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str,
    participant_id: int,
    #valid_session: bool = Depends(check_request_session) # <- Need to add auth to websockets later
):
    await websocket_manager.connect(websocket, session_id, participant_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.send_personal_message(f"You wrote: {data}", websocket)
            await websocket_manager.broadcast(f"Client #{participant_id} says: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id, websocket)
        await websocket_manager.broadcast(f"Client #{participant_id} left the chat")
