"""
Instead of splitting project related things into a different screen,
we are for the sake of simplicity, only updating the widget when username
has been submitted.
"""
from enum import Enum

import aiohttp
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, MaskedInput, Label, Input
from textual.containers import Vertical
from textual.events import Key
from textual.reactive import Reactive

from screens.management import ManagementScreen
from utils.session_manager import session_manager

ASCII_TITLE = """
_   _             _ _____ _   _ ___ 
| \ | | ___  _ __ (_)_   _| | | |_ _|
|  \| |/ _ \| '_ \| | | | | | | || | 
| |\  | (_) | | | | | | | | |_| || | 
|_| \_|\___/|_| |_|_| |_|  \___/|___|
"""

class ProjectType(Enum):
    """Enum for project types."""
    JOIN = 1
    CREATE = 2
    NONE = 3

class SessionScreen(Screen):
    """Screen for joining and creating sessions."""
    session_username: Reactive[str] = Reactive("")
    new_project_name: Reactive[str] = Reactive("")
    new_project_uuid: Reactive[str] = Reactive("")
    join_project_uuid: Reactive[str] = Reactive("")
    project_type: Reactive[ProjectType] = Reactive(ProjectType.NONE)

    def __init__(self):
        super().__init__()
        self._running = False

    CSS_PATH = "../styles/session.tcss"

    # Notifications here are probably unnecessary even though they look cool
    async def create_project(self, project_name: Reactive[str]):
        """Creates a new project and generates a session for the creator."""
        content = {"project_name": project_name}
        try:
            session = await session_manager.get_session()
            async with session.post("http://localhost:8000/projects/", json=content) as response:
                if response.status == 201:
                    session_id = await response.text()
                    return session_id.strip('"')
                else:
                    error_message = await response.text()
                    self.notify(f"Failed to create project: {error_message}")
                    return None
        except aiohttp.ClientConnectorError as e:
            self.notify(f"Connection Error: {e}")
        except Exception as e:
            self.notify(f"An unexpected error occurred: {str(e)}")

    # doing handlers later
    async def join_project(self, project_uuid, username):
        """Joins a project"""
        try:
            session = await session_manager.get_session()
            async with session.post(
                    f"http://localhost:8000/projects/join/{project_uuid}?username={username}"
            ) as response:
                
                if response.status == 200:
                    session_id = await response.text()
                    self.notify(f"Successfully joined the project!")
                    return session_id
                else:
                    error_message = await response.text()
                    self.notify(f"Failed to join project: {error_message}")
                    return None
        except aiohttp.ClientConnectorError as e:
            self.notify(f"Connection Error {e.__str__()}")
        except Exception as e:
            self.notify(f"An unexpected error occurred: {str(e)}")

    def compose(self) -> ComposeResult:
        # PROJECT TITLE
        self.submit_label = Label("Go (Enter)", id="session-submit-help")

        # PROJECT RELATED
        self.join_project_label = Label("Join project by entering its UUID")
        self.project_not_found = Label("Sorry! Can't find projects with your UUID.", classes="remove")
        self.join_project_input = Input(
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
            classes="remove"
        )
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
                self.session_username = self.username_input.value.strip()
                match self.project_type:
                    case ProjectType.JOIN:
                        await self.join_project(self.join_project_uuid, self.session_username)
                        await self.app.push_screen(ManagementScreen(project_uuid=self.join_project_uuid))
                    case ProjectType.CREATE:
                        await self.join_project(self.new_project_uuid, self.session_username)
                        await self.app.push_screen(ManagementScreen(project_uuid=self.new_project_uuid))
            elif self.join_project_input.has_focus:
                self.project_type = ProjectType.JOIN
                self.join_project_uuid = self.join_project_input.value.strip()
                self.widget_swap_from_project_to_username()
            elif self.create_project_input.has_focus:
                self.project_type = ProjectType.CREATE
                self.new_project_name = self.create_project_input.value.strip()
                self.new_project_uuid = await self.create_project(self.new_project_name)
                self.widget_swap_from_project_to_username()

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
