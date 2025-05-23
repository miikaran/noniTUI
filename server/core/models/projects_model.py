from core.sql_interface import SQLInterface
from datetime import datetime

class ProjectsModel(SQLInterface):
    def __init__(self, db_conn):
        super().__init__(db_conn)
        self.set_table("projects")
        self.set_autofilled_columns([
            ("project_id", int)
        ])
        self.set_columns([
            ("project_name", str),
            # No need, for now.
            # ("description", str),
            ("created_at", datetime),
            ("modified_at", datetime)
        ])
        self.set_clauses({
            "projects_equals_in": "{} in {}",
            "projects_equals": "{} = {}"
        })
