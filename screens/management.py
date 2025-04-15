import asyncio
import aiohttp
from datetime import datetime
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Vertical
from textual.widgets import Static, TabbedContent, TabPane, Input, Button, Label
from textual.reactive import reactive
from textual import events
from version import __version__
from widgets.message import Message
from utils.session_manager import session_manager


class TaskEditModalScreen(Screen):
    """A modal screen for editing tasks"""
    class Submit(Message):
        def __init__(self, sender, task_id, data):
            self.task_id = task_id
            self.data = data
            super().__init__(sender)

    def __init__(self, task_data: dict, parent_screen):
        super().__init__()
        self.task_data = task_data
        self.parent_screen = parent_screen
        self._visible = reactive(False)

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Edit Task", id="modal-title"),
            Input(value=self.task_data.get("name", ""), id="input-name", placeholder="Name"),
            Input(value=self.task_data.get("assignee", ""), id="input-assignee", placeholder="Assignee"),
            Input(value=self.task_data.get("description", ""), id="input-description", placeholder="Description"),
            Input(value=self.task_data.get("task_type", ""), id="input-type", placeholder="Task Type"),
            Button("Save", id="save-btn"),
            Button("Cancel", id="cancel-btn")
        )

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save-btn":
            # Handle save and submit the form data
            data = {
                "name": self.query_one("#input-name", Input).value,
                "assignee": self.query_one("#input-assignee", Input).value,
                "description": self.query_one("#input-description", Input).value,
                "task_type": self.query_one("#input-type", Input).value,
            }
            await self.post_message(self.Submit(self, self.task_data["id"], data))
            await self.cancel()
        elif event.button.id == "cancel-btn":
            await self.cancel() 

    async def cancel(self):
        """Handle modal cancellation."""
        self.app.pop_screen()

    async def on_mount(self) -> None:
        """Show the modal when it's mounted."""
        self._visible = True
        self.update_visibility()

    def update_visibility(self):
        if self._visible:
            self.add_class("modal-visible")
            self.remove_class("modal-hidden")
        else:
            self.add_class("modal-hidden")
            self.remove_class("modal-visible")

    def render(self) -> str:
        if self._visible:
            return super().render()
        else:
            return "" 


class TaskWidget(Static):
    task_data = reactive({})
    expanded = reactive(False)
    selected = reactive(False)

    def __init__(self, task_data, parent_screen):
        super().__init__()
        self.task_data = task_data
        self.parent_screen = parent_screen
        self.add_class("task-widget")

    def can_focus(self) -> bool:
        return True

    def render(self) -> str:
        name = self.task_data.get("name", "Unknown")
        assignee = self.task_data.get("assignee", "Unknown")
        start = self.format_date(self.task_data.get("start_date", "N/A"))
        end = self.format_date(self.task_data.get("end_date", "N/A"))
        basic_info = f"{name} | {assignee} | {start} → {end}"
        if self.selected:
            basic_info = f"[b]{basic_info}[/b]"
            self.add_class("selected")
        else:
            self.remove_class("selected")
        if self.expanded:
            description = self.task_data.get("description", "No description")
            task_type = self.task_data.get("task_type", "todo")
            more_info = f"\n\nDescription: {description}\nTask Type: {task_type}\n"
            return basic_info + more_info
        else:
            return basic_info

    async def on_click(self) -> None:
        self.focus()
        self.expanded = not self.expanded
        self.update(self.render())

    async def on_key(self, event: events.Key) -> None:
        if event.key == "e": 
            await self.parent_screen.show_task_edit_modal(self.task_data)
        elif event.key == "enter": 
            self.expanded = not self.expanded
            self.update(self.render())
        elif event.key == "up" or event.key == "down":
            self.selected = not self.selected
            self.update(self.render())

    def format_date(self, date_string: str) -> str:
        """Format the date string to a more readable format"""
        try:
            date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
            return date_obj.strftime("%b %d, %Y %H:%M")
        except ValueError:
            return date_string


class TaskList(Container):
    """Container to manage the list of tasks and keyboard navigation."""
    def __init__(self, parent_screen):
        super().__init__()
        self.task_widgets = []
        self.parent_screen = parent_screen

    def add_task(self, task_widget: TaskWidget):
        self.task_widgets.append(task_widget)
        self.mount(task_widget)

    def can_focus(self) -> bool:
        return True

    async def on_mount(self) -> None:
        self.focus()
        if len(self.task_widgets) > 0:
            self.task_widgets[0].selected = True
            self.task_widgets[0].update(self.task_widgets[0].render())

    async def on_key(self, event: events.Key) -> None:
        if not self.task_widgets:
            return
        if event.key == "up":
            for i, task_widget in enumerate(self.task_widgets):
                if task_widget.selected:
                    task_widget.selected = False
                    if i > 0:
                        self.task_widgets[i - 1].selected = True
                        self.task_widgets[i - 1].update(self.task_widgets[i - 1].render())
                        self.task_widgets[i - 1].focus()
                    else:
                        self.task_widgets[i].selected = True
                        self.task_widgets[i].update(self.task_widgets[i].render())
                        self.task_widgets[i].focus()
                    break
        elif event.key == "down":
            for i, task_widget in enumerate(self.task_widgets):
                if task_widget.selected:
                    task_widget.selected = False
                    if i < len(self.task_widgets) - 1:
                        self.task_widgets[i + 1].selected = True
                        self.task_widgets[i + 1].update(self.task_widgets[i + 1].render())
                        self.task_widgets[i + 1].focus()
                    else:
                        self.task_widgets[i].selected = True
                        self.task_widgets[i].update(self.task_widgets[i].render())
                        self.task_widgets[i].focus()
                    break
        else:
            for task_widget in self.task_widgets:
                if task_widget.selected:
                    task_widget.focus() 
                    await task_widget.on_key(event)


class ManagementScreen(Screen):
    def __init__(self, project_uuid):
        super().__init__()
        self.project_uuid = project_uuid
        self.task_edit_modal = None
        self._running = False

    CSS_PATH = [
        "../styles/management.tcss",
        "../styles/message.tcss",
        "../styles/task.tcss"
    ]

    async def on_mount(self):
        try:
            session = await session_manager.get_session()
            await self.fetch_project_tasks(session)
        except aiohttp.ClientError as e:
            self.notify(f"Connection Error: {e}")
        except Exception as e:
            self.notify(f"Unexpected error: {str(e)}")

    async def fetch_project_tasks(self, session):
        """Fetch tasks of the project session"""
        url = f"http://localhost:8000/tasks"
        async with session.get(url) as response:
            if response.status == 200:
                tasks = await response.json()
                await self.populate_tasks(tasks)
            else:
                self.notify(f"Failed to fetch tasks: {response.status}")

    async def populate_tasks(self, tasks_data: list[dict]):
        """Populate the UI with tasks categorized by task_type."""
        backlog = self.query_one("#backlog-tabpane", TabPane)
        todo = self.query_one("#todo-tabpane", TabPane)
        in_progress = self.query_one("#in-progress-tabpane", TabPane)
        done = self.query_one("#done-tabpane", TabPane)
        containers = {
            "backlog": backlog.query_one(VerticalScroll),
            "todo": todo.query_one(VerticalScroll),
            "in-progress": in_progress.query_one(VerticalScroll),
            "done": done.query_one(VerticalScroll)
        }
        for container in containers.values():
            await self.remove_widgets_from_container(container)
        task_lists = {
            "backlog": TaskList(self),
            "todo": TaskList(self),
            "in-progress": TaskList(self),
            "done": TaskList(self),
        }
        for task_type, task_list in task_lists.items():
            containers[task_type].mount(task_list)
        for task in tasks_data:
            raw_type = task.get("task_type", "backlog")
            task_type = raw_type if raw_type in task_lists else "backlog"
            task_widget = TaskWidget(task_data=task, parent_screen=self)
            task_lists[task_type].add_task(task_widget)

    async def remove_widgets_from_container(self, container):
        """Remove widgets from container"""
        for widget in container.children:
            container.remove(widget)

    async def show_task_edit_modal(self, task_data):
        """Show the task edit modal screen."""
        modal_screen = TaskEditModalScreen(task_data=task_data, parent_screen=self)
        self.app.push_screen(modal_screen) 

    def compose(self) -> ComposeResult:
        with Container(id="app-grid"):
            with Container(id="information-bar"):
                yield Horizontal(Static(f"Noni {__version__}", id="noni-text"))
            with VerticalScroll(id="chat-left-pane"):
                yield Message()
            with Container(id="tasks-top-right"):
                with TabbedContent(initial="backlog-tabpane"):
                    with TabPane("Backlog", id="backlog-tabpane"):
                        yield VerticalScroll()
                    with TabPane("Todo", id="todo-tabpane"):
                        yield VerticalScroll()
                    with TabPane("In-Progress", id="in-progress-tabpane"):
                        yield VerticalScroll()
                    with TabPane("Done", id="done-tabpane"):
                        yield VerticalScroll()
        return super().compose()
