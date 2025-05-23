from core.sql_interface import SQLInterface
from datetime import datetime

class MessagesModel(SQLInterface):
    def __init__(self, db_conn):
        super().__init__(db_conn)
        self.set_table("messages")
        self.set_autofilled_columns([
            ("id", int)
        ])
        self.set_columns([
            ("project_id", int),
            #("session_participant_id", int),
            ("message_sender", str),
            ("message_content", str),
            ("message_timestamp", datetime)
        ])
        self.set_clauses({
            "messages_equals_in": "{} in {}",
            "messages_equals": "{} = {}"
        })