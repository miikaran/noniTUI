from sql_interface import SQLInterface

class ProjectsModel(SQLInterface):
    def __init__(self, db_conn):
        super().__init__(db_conn)
        self.set_table("projects")
        self.set_columns([
            ("project_id", int),
            ("project_name", str),
            ("description", str),
            ("created_at", str),
            ("modified_at", str)
        ])
        self.set_clauses({
            "projects_equals_in": "{} in {}",
            "projects_equals": "{} = {}"
        })