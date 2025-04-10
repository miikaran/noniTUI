from textual.app import App, ComposeResult, RenderResult
from textual.widget import Widget
from textual.screen import Screen
from textual.widgets import Static

class Session(Screen):
    CSS = """
        Screen {
            align: center middle;
        }
    """

    def compose(self) -> ComposeResult:
        yield Static("NoniTUI", id="title")
