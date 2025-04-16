import aiohttp
from datetime import datetime
from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.containers import Container, Horizontal, VerticalScroll, Vertical
from textual.widgets import Static, TabbedContent, TabPane, Input, Button, Label, ListView, ListItem
from textual.reactive import reactive
from textual import events
from version import __version__
from widgets.message import Message
from utils.session_manager import session_manager


class TaskEditModalScreen(ModalScreen):
    def __init__(self, task_data: dict, parent_screen):
        super().__init__()
        self.task_data = task_data
        self.parent_screen = parent_screen
        self._visible = reactive(False)

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"Edit Task {self.task_data.get('id')}", id="modal-title"),
            Input(value=self.task_data.get("name", ""), id="input-name", placeholder="Name"),
            Input(value=self.task_data.get("assignee", ""), id="input-assignee", placeholder="Assignee"),
            Input(value=self.task_data.get("description", ""), id="input-description", placeholder="Description"),
            Input(value=self.task_data.get("task_type", ""), id="input-type", placeholder="Task Type"),
            Input(value=self.task_data.get("start_date", ""), id="input-start", placeholder="Start date - YYYYMMDD"),
            Input(value=self.task_data.get("end_date", ""), id="input-end", placeholder="End date - YYYYMMDD"),
            Button("Submit", id="save-btn"),
            Button("Cancel", id="cancel-btn")
        )

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save-btn":
            self.task_data["name"] = self.query_one("#input-name", Input).value
            self.task_data["assignee"] = self.query_one("#input-assignee", Input).value
            self.task_data["description"] = self.query_one("#input-description", Input).value
            self.task_data["task_type"] = self.query_one("#input-type", Input).value
            self.task_data["start_date"] = self.query_one("#input-start", Input).value
            self.task_data["end_date"] = self.query_one("#input-end", Input).value
            await self.submit_form()
            await self.cancel()
        elif event.button.id == "cancel-btn":
            await self.cancel()

    async def submit_form(self):
        try:
            session = await session_manager.get_session()
            task_id = self.task_data["id"]
            url = f"http://localhost:8000/tasks/{task_id}"
            async with session.put(url, json=self.task_data) as response:
                if response.status == 200:
                    self.app.notify("Task updated successfully.")
                else:
                    self.app.notify(f"Failed to update task: {response.status}")
        except Exception as e:
            self.app.notify(f"Error during update: {str(e)}")

    async def cancel(self):
        self.app.pop_screen()

    async def on_mount(self):
        self._visible = True
        self.update_visibility()

    def update_visibility(self):
        if self._visible:
            self.add_class("modal-visible")
            self.remove_class("modal-hidden")
        else:
            self.add_class("modal-hidden")
            self.remove_class("modal-visible")


class TaskWidget(ListItem):
    task_data = reactive({})
    expanded = reactive(False)
    selected = reactive(False)

    def __init__(self, task_data, parent_screen):
        super().__init__()
        self.task_data = task_data
        self.parent_screen = parent_screen

    def can_focus(self) -> bool:
        return True 

    def compose(self) -> ComposeResult:
        yield Static(self.render_text(), id="task-static")

    def render_text(self):
        name = self.task_data.get("name", "Unknown")
        assignee = self.task_data.get("assignee", "Unknown")
        start = self.format_date(self.task_data.get("start_date", "N/A"))
        end = self.format_date(self.task_data.get("end_date", "N/A"))
        basic_info = f"{name} | {assignee} | {start} → {end}"
        if self.expanded:
            description = self.task_data.get("description", "No description")
            more_info = f"\nDescription: {description}"
            return basic_info + more_info
        return basic_info

    def watch_selected(self, value: bool):
        if value:
            self.add_class("selected-task")
        else:
            self.remove_class("selected-task")

    def toggle_move_mode(self, move_mode):
        if move_mode:
            self.app.notify(f"Task {self.task_data.get('id')} move mode on")
            self.add_class("move-mode")
        else:
            self.app.notify(f"Task {self.task_data.get('id')} move mode off")
            self.remove_class("move-mode")

    async def on_click(self):
        self.expanded = not self.expanded
        self.query_one("#task-static", Static).update(self.render_text())

    def format_date(self, date_string: str) -> str:
        try:
            date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
            return date_obj.strftime("%b %d, %Y %H:%M")
        except ValueError:
            return date_string


class TaskList(ListView):
    def __init__(self, parent_screen):
        super().__init__()
        self.parent_screen = parent_screen
        self.selected_item = None
        self.move_mode = False

    def add_task(self, task_widget: TaskWidget):
        self.append(task_widget)

    async def on_key(self, event: events.Key):
        if event.key == "up":
            self.select_previous_item()
            event.stop()
        elif event.key == "down":
            self.select_next_item()
            event.stop()
        elif event.key == "e":
            if self.selected_item:
                await self.parent_screen.show_task_edit_modal(self.selected_item.task_data)
            event.stop()
        elif event.key == "enter":
            if self.selected_item:
                await self.selected_item.on_click()
            event.stop()
        elif event.key in ("left", "right") and self.move_mode:
            await self.parent_screen.move_task(self.selected_item, event.key)
            event.stop()
        elif event.key == "m": 
            self.move_mode = not self.move_mode
            if self.selected_item:
                self.selected_item.selected = self.move_mode
                self.selected_item.toggle_move_mode(self.move_mode)
            self.selected_item.watch_selected(bool(self.selected_item))
            event.stop()
        elif event.key == "d":
            if self.selected_item:
                await self.parent_screen.delete_task(self.selected_item.task_data)
            event.stop()

    def select_previous_item(self):
        if self.selected_item:
            index = self.children.index(self.selected_item) - 1
            if index >= 0:
                self.select_item(self.children[index])

    def select_next_item(self):
        if self.selected_item:
            index = self.children.index(self.selected_item) + 1
            if index < len(self.children):
                self.select_item(self.children[index])

    def select_item(self, widget: TaskWidget):
        if self.selected_item and self.selected_item != widget:
            self.selected_item.selected = False
        self.selected_item = widget
        widget.selected = True
        self.app.set_focus(widget)

    def get_selected(self):
        return self.selected_item

    def get_widget_at(self, index: int):
        return self.children[index]


class ManagementScreen(Screen):
    focused_pane = reactive("chat")

    def __init__(self, project_uuid):
        super().__init__()
        self.project_uuid = project_uuid
        self.task_lists = {}

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
        self.update_focus_borders()
        self.update_footer_shortcuts()

    def update_focus_borders(self):
        chat = self.query_one("#chat-left-pane", Vertical)
        tasks = self.query_one("#tasks-top-right", Container)
        if self.focused_pane == "chat":
            chat.add_class("focused-pane")
            tasks.remove_class("focused-pane")
            self.set_focus(chat)
        else:
            tasks.add_class("focused-pane")
            chat.remove_class("focused-pane")
            current_tab = self.query_one(TabbedContent).active
            task_list = self.task_lists.get(current_tab.replace("-tabpane", ""))
            if task_list:
                self.set_focus(task_list)

    async def on_key(self, event: events.Key):
        if event.key == "tab":
            self.focused_pane = "chat" if self.focused_pane == "tasks" else "tasks"
            self.update_focus_borders()
            self.update_footer_shortcuts()
            event.stop()
        elif self.focused_pane == "tasks":
            current_tab = self.query_one(TabbedContent).active
            task_list = self.task_lists.get(current_tab.replace("-tabpane", ""))
            if task_list:
                await task_list.on_key(event)

    async def fetch_project_tasks(self, session):
        url = f"http://localhost:8000/tasks"
        async with session.get(url) as response:
            if response.status == 200:
                tasks = await response.json()
                await self.populate_tasks(tasks)
                self.app.notify("Tasks fetched for the project.")
            else:
                self.notify(f"Failed to fetch tasks: {response.status}")

    async def populate_tasks(self, tasks_data: list[dict]):
        tabs = {
            "backlog": self.query_one("#backlog-tabpane", TabPane).query_one(ListView),
            "todo": self.query_one("#todo-tabpane", TabPane).query_one(ListView),
            "in-progress": self.query_one("#in-progress-tabpane", TabPane).query_one(ListView),
            "done": self.query_one("#done-tabpane", TabPane).query_one(ListView)
        }
        self.task_lists = tabs
        for lv in tabs.values():
            lv.clear()
        for task in tasks_data:
            task_type = task.get("task_type", "backlog").lower()
            task_type = task_type if task_type in tabs else "backlog"
            widget = TaskWidget(task, self)
            tabs[task_type].append(widget)
            if len(tabs[task_type].children) == 1:
                tabs[task_type].select_item(widget)

    async def move_task(self, task_widget: TaskWidget, direction: str):
        order = ["backlog", "todo", "in-progress", "done"]
        current_type = task_widget.task_data.get("task_type", "backlog").lower()
        try:
            index = order.index(current_type)
            new_index = index + 1 if direction == "right" else index - 1
            if 0 <= new_index < len(order):
                new_type = order[new_index]
                task_id = task_widget.task_data["id"]
                session = await session_manager.get_session()
                url = f"http://localhost:8000/tasks/{task_id}"
                data = {
                    "name": task_widget.task_data.get("name", ""),
                    "assignee": task_widget.task_data.get("assignee", ""),
                    "description": task_widget.task_data.get("description", ""),
                    "task_type": new_type,
                    "start_date": task_widget.task_data.get("start_date", ""),
                    "end_date": task_widget.task_data.get("end_date", "")
                }
                async with session.put(url, json=data) as response:
                    if response.status == 200:
                        task_widget.task_data["task_type"] = new_type
                        self.notify(f"Moved task {task_widget.task_data.get('id')} to '{new_type}'.")
                    else:
                        self.notify(f"Failed to move task {task_widget.task_data.get('id')}: {response.status}")
        except Exception as e:
            self.notify(f"Error moving task: {str(e)}")

    async def show_task_edit_modal(self, task_data):
        modal_screen = TaskEditModalScreen(task_data=task_data, parent_screen=self)
        self.app.push_screen(modal_screen)

    async def delete_task(self, task_data):
        try:
            task_id = task_data["id"]
            session = await session_manager.get_session()
            url = f"http://localhost:8000/tasks/{task_id}"
            async with session.delete(url) as response:
                if response.status == 200:
                    self.notify(f"Task {task_id} deleted successfully.")
                else:
                    self.notify(f"Failed to delete task {task_id}: {response.status}")
        except Exception as e:
            self.notify(f"Error deleting task: {str(e)}")

    def update_footer_shortcuts(self):
        footer = self.query_one("#shortcut-hints", Static)
        if self.focused_pane == "chat":
            footer.update("Tab - Switch Pane  |  ⬆/⬇ - Navigate Messages  |  Enter - Send Message")
        else:
            footer.update("M - Toggle Move Mode  |  ←/→ - Move Task  |  D - Delete Task  |  Tab - Switch Pane  |  ⬆/⬇ - Navigate Tasks")

    def compose(self) -> ComposeResult:
        with Container(id="app-grid"):
            with Container(id="information-bar"):
                yield Horizontal(Static(f"Noni {__version__}", id="noni-text"))
            with Vertical(id="chat-left-pane"):
                with VerticalScroll(id="chat-messages"):
                    yield Message()
                yield Input(placeholder="Type your message...", id="chat-input")
            with Container(id="tasks-top-right"):
                with TabbedContent(initial="backlog-tabpane"):
                    with TabPane("Backlog", id="backlog-tabpane"):
                        yield TaskList(self)
                    with TabPane("Todo", id="todo-tabpane"):
                        yield TaskList(self)
                    with TabPane("In-Progress", id="in-progress-tabpane"):
                        yield TaskList(self)
                    with TabPane("Done", id="done-tabpane"):
                        yield TaskList(self)
        with Container(id="footer"):
            yield Static("", id="shortcut-hints")
        return super().compose()
