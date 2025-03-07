from sql_interface import SQLInterface

class TasksModel(SQLInterface):
    def __init__(self, db_conn):
        super().__init__(db_conn)
        self.set_table("tasks")
        self.set_columns([
            ("id", int),
            ("project_id", int),
            ("name", str),
            ("assignee", str),
            ("description", str),
            ("start_date", str),
            ("end_date", str),
            ("task_type", str)
        ])
        self.set_clauses({
            "tasks_equals_in": "{} in {}",
            "tasks_equals": "{} = {}"
        })