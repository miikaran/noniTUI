from datetime import datetime
from textual.app import ComposeResult
from textual.widgets import Label, Static, ListItem

class Message(ListItem):
    def __init__(self, message_time, message_sender, message_content):
        super().__init__()
        self.message_time = message_time
        self.message_sender = message_sender
        self.message_content = message_content

    def compose(self) -> ComposeResult:
        yield Static(f"{self.message_time}", id="chat-message-time")
        yield Static(f"{self.message_sender}", id="chat-message-sender")
        yield Static(f"{self.message_content}", id="chat-message-content")
