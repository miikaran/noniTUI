from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label
from textual.containers import Container, Horizontal

class Message(Widget):
    def __init__(self):
        super().__init__()
        self.message_time = "10:45"  # TODO: Get actual message time.
        self.message_sender = "Anonymous"  # TODO: Get actual message sender.
        self.message_content = "Hi! This is a test"  # TODO: Get actual message content.

    def compose(self) -> ComposeResult:
        with Container(id="chat-message"):
            yield Horizontal(
                Label(f"{self.message_time}", id="chat-message-time"),
                Label(f"{self.message_sender}", id="chat-message-sender"),
                Label(f"{self.message_content}", id="chat-message-content")
            )
