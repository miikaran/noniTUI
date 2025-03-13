from sql_interface import SQLInterface
from models import projects_model, messages_model, tasks_model
from dotenv import load_dotenv
import os

load_dotenv()

postgresql_wrapped_credentials = {
    "user": os.getenv('POSTGRE_USERNAME'),
    "password": os.getenv('POSTGRE_PASSWORD'),
    "host": os.getenv('POSTGRE_HOST'),
    "port": os.getenv('POSTGRE_PORT'),
    "database": os.getenv('POSTGRE_DATABASE')
}

class Factories:
    @staticmethod
    def request_handler_factory(request_type, params):
        handlers = {
            "database_update": AppDatabaseHandler(
                params.get("statement_params"),
                params.get("target_table"),
                params.get("modification_type"),
                postgresql_wrapped_credentials,
            )
        }
        return handlers.get(request_type)

    @staticmethod
    def table_model_factory(table_type):
        table_models = {
            "projects": projects_model.ProjectsModel,
            "messages": messages_model.MessagesModel,
            "tasks": tasks_model.TasksModel,
            "sessions": None,
            "session_participants": None,
            "tasks_enrichment": None,
        }
        return table_models.get(table_type)

    
class AppDatabaseHandler:
    def __init__(self, statement_params, target_table, modification_type, postgresql_credentials):
        self.statement_params = statement_params
        self.target_table = target_table
        self.modification_type = modification_type
        self.database_connection = SQLInterface.init_db_conn(**postgresql_credentials)
        self.table_interface = Factories.table_model_factory(target_table)
        self.modification_type_to_handler = {
            "insert": self.table_interface.add,
            "select": self.table_interface.get,
            "update": self.table_interface.update,
            "delete": self.table_interface.delete,
        }
    
    def set_table(self, table):
        self.target_table = table
        self.table_interface = Factories.table_model_factory(table)
    
    def set_modification_type(self, type):
        self.modification_type = type
    
    def set_statement_params(self, params):
        self.statement_params = params

    def handle_request(self):
        model = self.table_interface
        if not model or not issubclass(model, SQLInterface):
            return False
        self.table_interface = self.table_interface(self.database_connection)
        if not self.table_interface:
            return False
        db_handler = self.modification_type_to_handler.get(
            self.modification_type,
            None
        ) 
        if not db_handler:
            return False
        results = db_handler(self.table_interface, params=self.statement_params) 
        self.database_connection.close()
        return results

    
        

    


    
    
        


    



