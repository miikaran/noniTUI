"""
Management screen is the screen where all the project management happens.
Modals are relevant in this screen.
"""
from textual.app import ComposeResult, RenderResult
from textual.screen import Screen
from textual.widgets import Static

class ManagementScreen(Screen):
    def __init__(self, project_uuid: str, new=True):
        super().__init__()
        self.project_uuid = project_uuid
        self._running = False

    def compose(self) -> ComposeResult:
        yield Static(f"Management Screen for Project: {self.project_uuid}")


