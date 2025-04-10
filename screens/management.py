from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Static, TabbedContent, TabPane

from version import __version__
from widgets.message import Message

class ManagementScreen(Screen):
    def __init__(self, project_uuid: str, new=True):
        super().__init__()
        self.project_uuid = project_uuid
        self._running = False

    CSS_PATH = [
        "../styles/management.tcss",
        "../styles/message.tcss",
    ]

    def compose(self) -> ComposeResult:
        with Container(id="app-grid"):
            with Container(id="information-bar"):
                yield Horizontal(
                    Static(f"Noni {__version__}", id="noni-text")
                    # Add other information, e.g., session users.
                )
            with VerticalScroll(id="chat-left-pane"):
                yield Message()
            with Container(id="tasks-top-right"):
                with TabbedContent(initial="backlog-tabpane"):
                    with TabPane("Backlog", id="backlog-tabpane"):
                        yield VerticalScroll(
                                Static("Implement chat | HIGH", classes="task"),
                                Static("Implement chat | HIGH", classes="task"),
                                Static("Implement chat | HIGH", classes="task"),
                        )
                    with TabPane("Todo", id="todo-tabpane"):
                        yield Static("Todo")
                    with TabPane("In-Progress", id="in-progress-tabpane"):
                        yield Static("In-Progress")
                    with TabPane("Done", id="done-tabpane"):
                        yield Static("Done")
