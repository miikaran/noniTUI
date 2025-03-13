from sql_interface import SQLInterface

class MessagesModel(SQLInterface):
    def __init__(self, db_conn):
        super().__init__(db_conn)
        self.set_table("messages")
        self.set_columns([
            ("project_id", int),
            ("session_participant_id", int),
            ("message_sender", str),
            ("message_content", str),
            ("message_timestamp", str)
        ])
        self.set_clauses({
            "messages_equals_in": "{} in {}",
            "messages_equals": "{} = {}"
        })