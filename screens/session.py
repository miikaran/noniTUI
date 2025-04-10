"""
Instead of splitting project related things into a different screen,
we are for the sake of simplicity, only updating the widget when username
has been submitted. 
"""
import uuid

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, MaskedInput, Label
from textual.containers import Vertical
from textual.events import Key

from screens.management import ManagementScreen

ASCII_TITLE = """
_   _             _ _____ _   _ ___ 
| \ | | ___  _ __ (_)_   _| | | |_ _|
|  \| |/ _ \| '_ \| | | | | | | || | 
| |\  | (_) | | | | | | | | |_| || | 
|_| \_|\___/|_| |_|_| |_|  \___/|___|
"""


class SessionScreen(Screen):
    """Screen for joining and creating sessions."""

    def __init__(self):
        super().__init__()
        self.session_username = None
        self.new_uuid = None
        self._running = False

    CSS_PATH = "../styles/session.tcss"

    def compose(self) -> ComposeResult:

        # PROJECT TITLE
        self.submit_label = Label("Go (Enter)", id="session-submit-help")

        # PROJECT RELATED
        self.join_project_label = Label("Join project by entering its UUID")
        self.project_not_found = Label("Sorry! Can't find projects with your UUID.", classes="remove")
        self.hex32 = "H" * 32
        self.join_project_input = MaskedInput(
            template=self.hex32,
            placeholder="123456e78-12e3-12e3-b123-12345e678bdb",
            id="join",
        )
        self.project_splitter = Label("OR", id="project-splitter")
        self.create_project_label = Label("Create a project by giving it a name")
        self.create_project_input = MaskedInput(
            template="n" * 25,
            placeholder="Project1",
            id="create",
        )

        # USERNAME RELATED
        self.username_label = Label("Enter a username that can be used to identify you in the project.",
                                    classes="remove")
        self.username_input = MaskedInput(
            template="a" * 60,
            placeholder="adalovelace",
            id="username",
            classes="remove"
        )

        # DISPLAY
        yield Vertical(Static(ASCII_TITLE, id="session-title"))
        yield Vertical(self.join_project_label)
        yield Vertical(self.join_project_input)
        yield Vertical(self.project_not_found)
        yield Vertical(self.project_splitter)
        yield Vertical(self.create_project_label)
        yield Vertical(self.create_project_input)
        yield Vertical(self.username_label)
        yield Vertical(self.username_input)
        yield Vertical(self.submit_label)

    async def on_key(self, event: Key):
        if event.key == "enter":
            if self.username_input.has_focus:
                self.session_username = self.username_input.value
                await self.app.push_screen(ManagementScreen())
            elif self.join_project_input.has_focus:
                await self.join_project()
            elif self.create_project_input.has_focus:
                await self.create_project()

    async def create_project(self):
        self.widget_swap_from_project_to_username()

    async def join_project(self):
        """Loads Management screen with data (can be empty)"""
        join_uuid = self.join_project_input.value
        match await self.project_exists(project_uuid=join_uuid):
            case True:
                self.widget_swap_from_project_to_username()
            case False:
                self.project_not_found.styles.display = "block"
                self.project_not_found.styles.color = "#ff757f"

    def widget_swap_from_project_to_username(self) -> None:
        """Swaps widgets, from project related to username related."""
        self.username_input.styles.display = "block"
        self.username_label.styles.display = "block"
        self.join_project_label.styles.display = "none"
        self.join_project_input.styles.display = "none"
        self.project_splitter.styles.display = "none"
        self.create_project_label.styles.display = "none"
        self.create_project_input.styles.display = "none"
        self.project_not_found.display = "none"
        self.username_input.focus()

    async def project_exists(self, project_uuid: uuid) -> bool:
        """Checks database for projects with the given uuid"""
        return True
