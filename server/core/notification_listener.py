from sql_interface import SQLInterface

class NotificationListener(SQLInterface):
    def __init__(self, db_conn, websocket_manager):
        super().__init__(db_conn)
        self.websocket_manager = websocket_manager
    
    def notifier_handler(self):
        pass

    def listener(self):
        pass

    def thread_wrapper(self):
        pass
