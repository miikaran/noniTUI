from fastapi import WebSocket
from typing import Dict

class WebsocketManager:
    def __init__(self):
        # Stored in format -> {<session_id>: {<participant_id>: WebSocket}}
        self.active_connections : Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str, participant_id: int):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        self.active_connections[session_id][str(participant_id)] = websocket

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
            if not session_participants:
                del self.active_connections[session_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for session_participants in self.active_connections.values():
            for websocket in session_participants.values():
                await websocket.send_text(message)


