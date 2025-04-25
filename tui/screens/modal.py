from textual.app import ComposeResult
from textual.containers import Horizontal, Container
from textual.screen import ModalScreen
from textual.widgets import Input, Label, TextArea, ListView, ListItem

class TaskModal(ModalScreen):
    """Modal screen for task creation with expandable ListView."""

    # Joku muu tekee tätä paskaa, en jaksa mitää tcss
    DEFAULT_CSS = """
        TaskModal {
            align: center middle;
        }

        #modal-parent-container {
            
            width: 70%;
            height: 70%;
            padding: 1;
            border: ascii #7dcfff;
            background: $surface 10%;
        }
    """

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(id="modal-parent-container"):
            with Container(id="modal-action-container"):
                yield Input(placeholder="Assigned to...", id="assignee")
                with Horizontal():
                    yield Input(placeholder="Start Date", id="start-date")
                    yield Input(placeholder="End Date", id="end-date")
                yield ListView(
                    ListItem(Label("Todo"), id="default-item"),
                    ListItem(Label("My text", name="My text")),
                    id="options",
                )
                yield Label("Nothing chosen",id="chosen")
                yield TextArea(id="description")
            with Container(id="modal-shortcut-container"):
                with Horizontal():
                    yield Label("Hide modal (Ctrl+h)")
                    yield Label("Submit (Ctrl+s)")

    # Nuo pikanäppäimetki saapi mainita, piilottaminen tapahtuu pop screenilla

    # Instead of notifying, it should set the task type
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        list_item = event.item.children[0]
        self.notify(f"{list_item.name}")
