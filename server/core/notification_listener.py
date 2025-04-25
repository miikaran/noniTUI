import asyncio
import json
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from core.utils.database import get_db
from concurrent.futures import ThreadPoolExecutor
import select

class NotificationListener():
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.active_tasks = {}
        self.session_id = None
        """
        Prefixes for LISTEN/NOTIFY channels, that we will listen to for data updates.
        When the first client joins a new session, we will add listener background tasks for each channel.
        The final channel name will be <table>_channel_<project_id>.
        """
        self.whitelisted_channels_prefixes = [
            "messages_channel_",
            "projects_channel_",
            "sessions_channel_",
            "tasks_channel_",
            "session_participants_channel_"
        ]

    def listen(self, channel, loop):
        conn = get_db()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f"LISTEN {channel};")
        print(f"Listening for messages on PostgreSQL channel '{channel}'...")
        while True:
            # Timeout to avoid blocking other code
            if select.select([conn], [], [], 5.0)[0]:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    print(f"Received PostgreSQL notification: {notify.payload}")
                    asyncio.run_coroutine_threadsafe(
                        self.handle_notification(notify.payload),
                        loop
                    )
            else:
                print("No notifications, continuing to poll")

    async def start_up(self, project_id, session_id=None):
        loop = asyncio.get_running_loop()
        for prefix in self.whitelisted_channels_prefixes:
            channel = f"{prefix}{project_id}"
            # Need to call this in another thread, because of the blocking nature
            future = self.executor.submit(self.listen, channel, loop)
            self.active_tasks[channel] = future
        if session_id:
            self.session_id = session_id
        loop.create_task(self.cleaner(interval_seconds=30*60))

    async def handle_notification(self, message: str):
        updated_row_json = json.loads(message)
        await self.websocket_manager.broadcast_to_session(updated_row_json, self.session_id)

    def should_cancel_channel(self, session_id):
        participants = self.websocket_manager.active_connections.get(session_id)
        return not participants 

    async def cleaner(self, interval_seconds=3600):
        while True:
            print("Running task cleanup")
            for channel, future in list(self.active_tasks.items()):
                if future.done():
                    print(f"Listening task for {channel} is done. Cleaning up.")
                    del self.active_tasks[channel]
                elif self.should_cancel_channel(self.session_id):
                    print(f"Cancelling task for {channel}. No active clients found.")
                    future.cancel()
                    del self.active_tasks[channel]
            await asyncio.sleep(interval_seconds)

    def shutdown(self):
        print("Shutting down thread pool executor.")
        self.executor.shutdown(wait=False)
