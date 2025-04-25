import websockets
import json
import asyncio

class WebSocketListener:
    def __init__(
            self, 
            screen,
            on_message_callback, 
            session_id: str, 
            session_participant_id: int, 
            max_retries: int = 5, 
            retry_interval: int = 5
            ):
        self.screen = screen
        self.on_message_callback = on_message_callback
        self.session_id = session_id
        self.session_participant_id = session_participant_id
        self.ws = None
        self.running = False
        self.max_retries = max_retries
        self.retry_interval = retry_interval

    async def start(self):
        ws_url = f"ws://localhost:8000/ws/{self.session_id}/{self.session_participant_id}" 
        retries = 0
        while retries < self.max_retries:
            try:
                async with websockets.connect(ws_url) as websocket:
                    self.ws = websocket
                    self.running = True
                    self.safe_notify("Connected to WebSocket")
                    while self.running:
                        try:
                            message = await websocket.recv()
                            await self.handle_websocket_message(message)
                            await asyncio.sleep(0.1)
                        except websockets.ConnectionClosed:
                            self.safe_notify("WebSocket connection closed.")
                            break
                        except asyncio.CancelledError:
                            break
                        except Exception as e:
                            self.safe_notify(f"Error receiving WebSocket message: {e}")
                break 
            except (websockets.exceptions.WebSocketException, ConnectionRefusedError) as e:
                self.safe_notify(f"WebSocket connection error: {e}")
            except Exception as e:
                self.safe_notify(f"Unexpected WebSocket error: {e}")            
            retries += 1
            if retries < self.max_retries:
                self.safe_notify(f"Retrying WebSocket connection in {self.retry_interval} seconds...")
                await asyncio.sleep(self.retry_interval)
            else:
                self.safe_notify("Max retries reached. Failed to connect to WebSocket.")
                break

    async def handle_websocket_message(self, message: str):
        try:
            self.safe_notify("Got new message")
            updated_data = json.loads(message)
            await self.on_message_callback(updated_data)
            await asyncio.sleep(0)
        except json.JSONDecodeError as e:
            print(f"Error decoding WebSocket message: {e}")
        except Exception as e:
            print(f"Unexpected error handling WebSocket message: {e}")

    async def safe_notify(self, message: str):
        try:
            if asyncio.iscoroutinefunction(self.screen.notify):
                await self.screen.notify(message)
            else:
                self.screen.notify(message)
        except Exception as e:
            print(f"Error notifying screen: {e}")

    async def close(self):
        self.running = False
        if self.ws:
            try:
                await self.ws.close()
            except websockets.exceptions.WebSocketException as e:
                print(f"Error closing WebSocket connection: {e}")
            except Exception as e:
                print(f"Unexpected error while closing WebSocket: {e}")
