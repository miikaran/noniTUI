import aiohttp
import asyncio
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
from utils.websocket_listener import WebSocketListener

def safe_async_call(func):
    # Global error handling to avoid crashing
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            self = args[0]
            if hasattr(self, "notify"):
                self.notify(f"Unexpected error in {func.__name__}: {str(e)}")
    return wrapper

class TaskEditModalScreen(ModalScreen):
    def __init__(self, task_data: dict, parent_screen):
        super().__init__()
        self.task_data = task_data
        self.parent_screen = parent_screen
        self._visible = reactive(False)
        self.is_new = self.task_data.get("id") is None

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Create Task" if self.is_new else f"Edit Task {self.task_data.get('id')}", id="modal-title"),
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
            if self.is_new:
                url = f"http://localhost:8000/tasks/new"
                async with session.post(url, json=self.task_data) as response:
                    if response.status == 200:
                        self.app.notify("Task created successfully.")
                    else:
                        self.app.notify(f"Failed to create task: {response.status}")
            else:
                task_id = self.task_data["id"]
                url = f"http://localhost:8000/tasks/{task_id}"
                async with session.put(url, json=self.task_data) as response:
                    if response.status == 200:
                        self.app.notify("Task updated successfully.")
                    else:
                        self.app.notify(f"Failed to update task: {response.status}")
        except Exception as e:
            self.app.notify(f"Error during task save: {str(e)}")

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
        id = self.task_data.get("id", "Unknown")
        name = self.task_data.get("name", "Unknown")
        assignee = self.task_data.get("assignee", "Unknown")
        start = self.format_date(self.task_data.get("start_date", "N/A"))
        end = self.format_date(self.task_data.get("end_date", "N/A"))
        basic_info = f"{id} - {name} | {assignee} | {start} → {end}"
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
        
    def update_task(self, new_data):
        self.task_data.update(new_data)
        self.query_one("#task-static", Static).update(self.render_text())


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
        elif event.key == "n":
            await self.parent_screen.show_task_edit_modal({})
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
                await self.parent_screen.delete_task(self.selected_item, self.selected_item.task_data)
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

    def get_widget_by_id(self, task_id: int):
        for widget in self.children:
            if widget.task_data.get("id") == task_id:
                return widget
        return None


class ManagementScreen(Screen):
    focused_pane = reactive("chat")

    def __init__(self, project_uuid, session_username, session_participant_id):
        super().__init__()
        self.project_uuid = project_uuid
        self.session_username = session_username
        self.session_participant_id = session_participant_id
        self.websocket_listener = WebSocketListener(
            self,
            self.on_websocket_message, 
            session_id=project_uuid, 
            session_participant_id=session_participant_id
            )
        self.task_lists = {}
        self.messages = {}
        self.participants = {}

    CSS_PATH = [
        "../styles/management.tcss",
        "../styles/message.tcss",
        "../styles/task.tcss"
    ]

    async def on_mount(self):
        try:
            session = await session_manager.get_session()
            await self.fetch_project_tasks(session)
            await self.fetch_project_messages()
            await self.fetch_participants(session)
            asyncio.create_task(self.websocket_listener.start())
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

    @safe_async_call
    async def on_key(self, event: events.Key):
        if event.key == "tab":
            self.focused_pane = "chat" if self.focused_pane == "tasks" else "tasks"
            self.update_focus_borders()
            self.update_footer_shortcuts()
            event.stop()
        elif self.focused_pane == "chat" and event.key == "enter":
            message_input = self.query_one("#chat-input", Input)
            message_content = message_input.value.strip()
            if message_content:
                await self.send_message(message_content)
                message_input.value = ""
            event.stop()
        elif self.focused_pane == "tasks":
            current_tab = self.query_one(TabbedContent).active
            task_list = self.task_lists.get(current_tab.replace("-tabpane", ""))
            if task_list:
                await task_list.on_key(event)

    @safe_async_call
    async def send_message(self, message_content: str):
        if not message_content.strip():
            return
        try:
            session = await session_manager.get_session()
            message_data = {
                "project_id": 62,
                "message_content": message_content,
                "message_sender": self.session_username,
                "message_timestamp": datetime.utcnow().isoformat(),
            }
            url = f"http://localhost:8000/messages/"
            async with session.post(url, json=message_data) as response:
                if response.status == 200:
                    self.notify("Message sent successfully.")
                else:
                    self.notify(f"Failed to send message: {response.status}")
        except Exception as e:
            self.notify(f"Error sending message: {str(e)}")

    @safe_async_call
    async def fetch_project_tasks(self, session):
        url = f"http://localhost:8000/tasks"
        async with session.get(url) as response:
            if response.status == 200:
                tasks = await response.json()
                await self.populate_tasks(tasks)
                self.app.notify("Tasks fetched for the project.")
            else:
                self.notify(f"Failed to fetch tasks: {response.status}")

    @safe_async_call
    async def fetch_participants(self, session):
        url = f"http://localhost:8000/projects/participants"
        async with session.post(url) as response:
            if response.status == 200:
                participants = await response.json()
                self.participants = {p['participant_id']: p['participant_name'] for p in participants}
                self.update_participant_container()
            else:
                self.notify(f"Failed to fetch participants: {response.status}")

    @safe_async_call
    async def fetch_project_messages(self):
        session = await session_manager.get_session()
        url = f"http://localhost:8000/messages"
        async with session.get(url) as response:
            if response.status == 200:
                all_messages = await response.json()
                if not all_messages:
                    self.use_default_chat_message()
                    return
                # Sort last 10 messages by time -> add to chat
                last_10 = sorted(all_messages, key=lambda m: m.get("message_timestamp", ""), reverse=True)[:10]
                last_10.reverse() 
                message_list = self.query_one("#chat-messages", ListView)
                message_list.clear()
                for msg in last_10:
                    widget = Message(
                        message_content=msg["message_content"],
                        message_sender=msg["message_sender"],
                        message_time=msg["message_timestamp"]
                    )
                    message_list.append(widget)
                message_list.scroll_end()
            else:
                self.notify(f"Failed to fetch messages: {response.status}")
                self.use_default_chat_message()

    @safe_async_call
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

    @safe_async_call
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
                    **task_widget.task_data,
                    "task_type": new_type
                }
                async with session.put(url, json=data) as response:
                    if response.status == 200:
                        self.notify(f"Moved task {task_widget.task_data.get('id')} to '{new_type}'.")
                        current_task_list = self.task_lists.get(current_type)
                        if current_task_list:
                            task_widget.remove()
                            current_task_list.move_mode = False
                            if len(current_task_list.children) > 0:
                                current_task_list.select_item(current_task_list.children[0])
                            else:
                                pass
                        new_widget = TaskWidget(task_widget.task_data.copy(), self)
                        new_task_list = self.task_lists.get(new_type)
                        if new_task_list:
                            new_task_list.append(new_widget)
                            current_index = new_task_list.children.index(new_widget)
                            new_task_list.select_item(new_widget)
                            new_task_list.move_mode = False
                    else:
                        self.notify(f"Failed to move task {task_widget.task_data.get('id')}: {response.status}")
        except Exception as e:
            self.notify(f"Error moving task: {str(e)}")

    @safe_async_call
    async def show_task_edit_modal(self, task_data):
        modal_screen = TaskEditModalScreen(task_data=task_data, parent_screen=self)
        self.app.push_screen(modal_screen)

    @safe_async_call
    async def delete_task(self, selected_item, task_data):
        try:
            task_id = task_data["id"]
            current_type = task_data.get("task_type", "backlog").lower()
            session = await session_manager.get_session()
            url = f"http://localhost:8000/tasks/{task_id}"
            async with session.delete(url) as response:
                if response.status == 200:
                    self.notify(f"Task {task_id} deleted successfully.")
                    current_task_list = self.task_lists.get(current_type)
                    current_index = current_task_list.children.index(selected_item)
                    if len(current_task_list.children) > 1:
                        if current_index > 0:
                            current_task_list.select_item(current_task_list.children[current_index - 1])
                        else:
                            current_task_list.select_item(current_task_list.children[1])                        
                else:
                    self.notify(f"Failed to delete task {task_id}: {response.status}")
        except Exception as e:
            self.notify(f"Error deleting task: {str(e)}")

    def update_footer_shortcuts(self):
        footer = self.query_one("#shortcut-hints", Static)
        if self.focused_pane == "chat":
            footer.update("Tab - Switch Pane  |  ⬆/⬇ - Navigate Messages  |  Enter - Send Message")
        else:
            footer.update("N - New Task  |  E - Edit  |  M - Move Mode  |  ←/→ - Move Task  |  D - Delete  |  Tab - Switch  |  ⬆/⬇ - Navigate")

    @safe_async_call
    async def on_websocket_message(self, updated_data):
        operation = updated_data.get("operation")
        table = updated_data.get("table")
        if operation == "INSERT":
            new_data = updated_data.get("new_data")
            if table == "tasks":
                self.handle_task_insert(new_data)
            elif table == "messages":
                self.handle_message_insert(new_data)
            elif table == "session_participants":
                self.handle_session_participant_insert(new_data)
            else:
                self.notify(f"Unsupported table operation: {table}")
        elif operation == "UPDATE":
            updated_data_entry = updated_data.get("updated_data")
            if table == "tasks":
                self.handle_task_update(updated_data_entry)
            elif table == "messages":
                self.handle_message_update(updated_data_entry) 
            elif table == "session_participants":
                self.handle_session_participant_update(updated_data_entry)
            else:
                self.notify(f"Unsupported table operation: {table}")
        elif operation == "DELETE":
            old_data = updated_data.get("old_data")
            if table == "tasks":
                self.handle_task_delete(old_data)
            elif table == "messages":
                self.handle_message_delete(old_data)
            elif table == "session_participants":
                self.handle_session_participant_delete(old_data)
            else:
                self.notify(f"Unsupported table operation: {table}")
        else:
            self.notify(f"Unsupported operation: {operation}")

    def handle_task_insert(self, new_data):
        task_type = new_data.get("task_type", "backlog")
        task_list = self.task_lists.get(task_type)
        if task_list:
            existing = task_list.get_widget_by_id(new_data["id"])
            if not existing:
                task_widget = TaskWidget(new_data, self)
                task_list.append(task_widget)
                if len(task_list.children) == 1:
                    task_list.select_item(task_widget)
                self.notify(f"Task {new_data['id']} added to '{task_type}'")
            else:
                self.notify(f"Task {new_data['id']} already exists")

    def handle_task_update(self, updated_data):
        new_type = updated_data.get("task_type", "backlog")
        task_id = updated_data.get("id")
        for current_type, current_task_list in self.task_lists.items():
            widget = current_task_list.get_widget_by_id(task_id)
            if widget:
                try:
                    current_index = current_task_list.children.index(widget)
                    widget.remove()
                    if len(current_task_list.children) > 1:
                        if current_index > 0:
                            current_task_list.select_item(current_task_list.children[current_index - 1])
                        else:
                            current_task_list.select_item(current_task_list.children[0])
                except ValueError:
                    pass
                break
        new_list = self.task_lists.get(new_type)
        if new_list:
            existing_widget = new_list.get_widget_by_id(task_id)
            if not existing_widget:
                new_widget = TaskWidget(updated_data, self)
                new_list.append(new_widget)
                if len(new_list.children) == 1:
                    new_list.select_item(new_widget)
            self.notify(f"Task {task_id} moved to '{new_type}'")

    def handle_task_delete(self, task_data):
        task_id = task_data["id"]
        task_type = task_data.get("task_type")
        task_list = self.task_lists.get(task_type)
        if task_list:
            widget = task_list.get_widget_by_id(task_id)
            if widget:
                widget.remove()  
                self.notify(f"Task {task_id} deleted from {task_type}")
                return

    def handle_message_insert(self, new_data):
        message_widget = Message(
            message_content=new_data.get("message_content", ""),
            message_sender=new_data.get("message_sender", "Unknown"),
            message_time=new_data.get("message_timestamp", "Unknown")
        )
        chat_messages = self.query_one("#chat-messages", ListView)
        chat_messages.append(message_widget)
        chat_messages.selected = message_widget 
        chat_messages.scroll_end()

    def handle_session_participant_insert(self, new_data):
        participant_id = new_data.get("participant_id")
        participant_name = new_data.get("participant_name")             
        self.participants[participant_id] = participant_name
        self.update_participant_container()
        self.notify(f"Participant {participant_name} added to session.")

    def handle_session_participant_update(self, updated_data):
        # no need for update in participants now
        pass

    def handle_session_participant_delete(self, old_data):
        participant_id = old_data.get("participant_id")
        participant_name = old_data.get("participant_name")
        if participant_id in self.participants:
            participant_name = self.participants.pop(participant_id)
            self.notify(f"Removed participant {participant_name} from session.")
            self.update_participant_container()
        else:
            self.notify(f"Participant with ID {participant_id} not found for removal.")

    def update_participant_container(self):
        participants_container = self.query_one("#participants-container", Container)
        for widget in participants_container.children:
            widget.remove()
        participant_names = ", ".join(self.participants.values())
        participants_widget = Static(participant_names)
        participants_widget.add_class("participant-names")
        participants_container.mount(participants_widget)

    def handle_message_update(self, updated_data):
        # No need for update to messages for now
        pass

    def handle_message_delete(self, old_data):
        # No need for deleting messages for now
        pass

    def use_default_chat_message(self):
        message_list = self.query_one("#chat-messages", ListView)
        message_list.clear()
        now = datetime.utcnow().isoformat(timespec='seconds')
        welcome = Message(
            message_content="This is a chat :)",
            message_sender="Anonymous",
            message_time=now
        )
        message_list.append(welcome)


    def compose(self) -> ComposeResult:
        with Container(id="app-grid"):
            with Container(id="information-bar"):
                yield Horizontal(Static(f"Noni {__version__}", id="noni-text"))
                yield Container(id="participants-container", classes="participants-container")
            with Vertical(id="chat-left-pane"):
                yield ListView(id="chat-messages")
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
