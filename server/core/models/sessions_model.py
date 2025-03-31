from core.sql_interface import SQLInterface
from datetime import datetime

class SessionsModel(SQLInterface):
    def __init__(self, db_conn):
        super().__init__(db_conn)
        self.set_table("sessions")
        self.set_columns([
            ("session_id", str),
            ("project_id", int),
            ("valid_until", datetime)
        ])
        self.set_clauses({
            "sessions_equals": "{} = {}"
        })

class SessionParticipantsModel(SQLInterface):
    def __init__(self, db_conn):
        super().__init__(db_conn)
        self.set_table("session_participants")
        self.set_columns([
            ("session_uuid", str),
            ("participant_name", str),
            ("joined_at", datetime)
        ])
        self.set_clauses({
            "session_participant_equals": "{} = {}",
            "session_participant_equals_in": "{} in {}"
        })