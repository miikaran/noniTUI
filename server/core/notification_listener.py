from core.sql_interface import SQLInterface
import asyncio
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

class NotificationListener(SQLInterface):
    def __init__(self, db_conn, websocket_manager):
        super().__init__(db_conn)
        self.websocket_manager = websocket_manager
        self.loop = asyncio.get_event_loop()
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.active_tasks = {}
        self.task_cleanup_interval_ms = 30 * (60 * 1000)
        """
        Prefixes for LISTEN/NOTIFY channels, that we will listen to for data updates.
        When the first client joins a new session, we will add listener background tasks for each channel.
        The final channel name will be <table>_channel_<project_id>.
        """
        self.whitelisted_channels_prefixes = [
            "messages_channel_",
            "projects_channel_"
            "sessions_channel_"
            "tasks_channel_",
            "session_participants_channel_"
        ]

    def handle_notification(self, notification):
        """This is replaced with the actual handler when initializing the listener"""
        print(notification)

    def listen(self, channel):
        self.cursor.execute(f"LISTEN {channel};")
        print(f"Listening for messages on PostgreSQL channel '{channel}'...")
        while True:
            self.conn.poll()
            while self.conn.notifies:
                notify = self.conn.notifies.pop(0)
                print(f"Received PostgreSQL notification: {notify.payload}")
                self.handle_notification(notify.payload)
                
    def start_up(self, project_id, session_id=None):
        for channel_prefix in self.whitelisted_channels_prefixes:
            final_channel_name = f"{channel_prefix}{project_id}"
            loop = asyncio.get_event_loop()
            task = loop.create_task(asyncio.to_thread(self.listen, channel=final_channel_name))
            self.active_tasks[final_channel_name] = task
            if session_id:
                # Store session id here as well to clean unnecessary tasks
                self.session_id = session_id
            # Add background task to clean hanging listening tasks
            loop.create_task(self.cleaner(interval_seconds=30*60))

    async def handle_notification(self, message: str):
        updated_row_json = json.loads(message)
        await self.websocket_manager.broadcast_to_session(updated_row_json)

    def should_cancel_channel(self, session_id):
        session_participants = self.websocket_manager.active_connections[session_id]
        return session_participants == True

    async def cleaner(self, interval_seconds=3600):
        while True:
            print("Running task cleanup")
            for channel, task in list(self.active_tasks.items()):
                if task.done():
                    print(f"Listening task for {channel} is done. Cleaning up.")
                    del self.active_tasks[channel]
                elif self.should_cancel_channel(self.session_id):
                    print(f"Cancelling task for {channel}. No active clients found.")
                    task.cancel()
                    del self.active_tasks[channel]
            await asyncio.sleep(interval_seconds)