from datetime import datetime
from textual.app import ComposeResult
from textual.widgets import Label, Static, ListItem

def time_ago(timestamp: str) -> str:
    try:
        if '.' in timestamp:
            timestamp = timestamp.split('.')[0]        
        message_time = datetime.fromisoformat(timestamp)
        now = datetime.utcnow()
        delta = now - message_time
        seconds = delta.total_seconds()
        if seconds < 30:
            return "Just now"
        elif seconds < 3600:
            return f"{int(seconds // 60)} min ago"
        elif seconds < 86400:
            return f"{int(seconds // 3600)} hour ago" if int(seconds // 3600) == 1 else f"{int(seconds // 3600)} hours ago"
        elif seconds < 2592000:
            return f"{int(seconds // 86400)} day ago" if int(seconds // 86400) == 1 else f"{int(seconds // 86400)} days ago"
        elif seconds < 31536000:
            return f"{int(seconds // 2592000)} month ago" if int(seconds // 2592000) == 1 else f"{int(seconds // 2592000)} months ago"
        else:
            return f"{int(seconds // 31536000)} year ago" if int(seconds // 31536000) == 1 else f"{int(seconds // 31536000)} years ago"
    except ValueError as e:
        return f"Invalid timestamp: {timestamp} - {str(e)}"

class Message(ListItem):
    def __init__(self, message_time, message_sender, message_content):
        super().__init__()
        self.message_time = message_time
        self.message_sender = message_sender
        self.message_content = message_content

    def compose(self) -> ComposeResult:
        relative_time = time_ago(self.message_time)        
        yield Static(f"Time: {relative_time}", id="chat-message-time")
        yield Static(f"Sender: {self.message_sender}", id="chat-message-sender")
        yield Static(f"Message: {self.message_content}", id="chat-message-content")
