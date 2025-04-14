from fastapi import WebSocket
from typing import Dict
from core.notification_listener import NotificationListener
from core.utils.database import get_db
from core.handlers import SessionHandler

class WebsocketManager:
    def __init__(self):
        # Stored in format -> {<session_id>: {<participant_id>: WebSocket}}
        self.active_connections : Dict[str, Dict[str, WebSocket]] = {}
        self.session_handler = SessionHandler(get_db())

    async def connect(self, websocket: WebSocket, session_id: str, participant_id: int):
        await websocket.accept()
        if not (session_id and participant_id):
            await websocket.send_text(f"Session ID or participant ID not found in path, byebye")
            await websocket.close(code=1000)
        if session_id not in self.active_connections:
            project_id = self.session_handler.get_session(session_id=session_id)[0]["project_id"]
            if not project_id:
                await websocket.send_text(f"Project ID not found for session ID: {session_id}, byebye")
                await websocket.close(code=1000)
            self.active_connections[session_id] = {}
            notification_listener = NotificationListener(
                db_conn=get_db(),
                websocket_manager=self,
            )
            await notification_listener.start_up(project_id, session_id=session_id)
        self.active_connections[session_id][str(participant_id)] = websocket
        print(f"#{participant_id} joined session {session_id} room")
        print(f"Current users in that room: {list(self.active_connections[session_id].keys())}")
        print(f"\nAll rooms and users {self.active_connections}")

    def disconnect(self, session_id: str,  websocket: WebSocket):
        if session_id in self.active_connections:
            session_participants = self.active_connections[session_id]
            participant_id_to_remove = None
            for participant_id, ws in session_participants.items():
                if ws == websocket:
                    participant_id_to_remove = participant_id
                    break
            if participant_id_to_remove is not None:
                del session_participants[participant_id_to_remove]
                print(f"#{participant_id_to_remove} disconnected from session {session_id}")
            if not session_participants:
                del self.active_connections[session_id]

    async def broadcast_to_session(self, message, session_id):
        if session_id not in self.active_connections:
            print(f"No session id of: {session_id} found for broadcasting")
            return False
        print(f"Broadcasting {message} to session: {session_id}")
        session_websockets = self.active_connections[session_id]
        if len(session_websockets) < 1:
            print(f"No websockets found in session {session_id}")
            print(f"Removing empty session room: {session_id}")
            del self.active_connections[session_id]
        for client, websocket in session_websockets.items():
            await websocket.send_json(message)
        print(f"Sent {message} to all {len(session_websockets)} members of session {session_id}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        print(f"Sending {message} to all active connections")
        for session_participants in self.active_connections.values():
            for websocket in session_participants.values():
                await websocket.send_text(message)


