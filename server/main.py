from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
import uvicorn
from api import projects, messages, tasks, websockets
from core.utils.exceptions import centralized_error_handling
from api.projects import check_request_session
from server.core.websocket_manager import WebsocketManager

"""
If the debug property is True, the errors raised during request handling will be returned to client by FastAPI by default,
and the centralized_error_handler won't work. If it is set to False, then it should handle exceptions properly.
"""
app = FastAPI(
    title="NoniAPI",
    debug=False
)
app.include_router(projects.router)
app.include_router(messages.router)
app.include_router(tasks.router)
app.include_router(websockets.router)

@centralized_error_handling
@app.get("/")
async def root():
    return "This is the root of Noni API"

if __name__ == "__main__":
    """Start the server with -> fastapi dev main.py"""
    uvicorn.run(
        app="main:app", 
        host="localhost", 
        port=8000,
        reload=True
    )