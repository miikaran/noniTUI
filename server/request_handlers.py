from sql_interface import SQLInterface
from models import projects_model, messages_model, tasks_model
from datetime import datetime, timedelta
import uuid

class AppDatabaseHandler:
    def __init__(self, target_table, postgresql_credentials, exception_cls):
        self.table = target_table
        self.db = SQLInterface.init_db_conn(**postgresql_credentials)
        self.model = self.table_model_factory(target_table)(self.db)
        self.exception_cls = exception_cls
    
    def change_table(self, table):
        self.table = table
        self.model = self.table_model_factory(table)(self.db)

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

    def already_exists(self, model, filter_params):
        query_result = model.get(params=[{
            **filter_params
        }])
        return query_result.length > 0

    def create_project(self, project_data):
        new_project_name = project_data.get("project_name", None)
        if not new_project_name:
            print("No project name found in params")
            return False
        project_already_exists = self.already_exists(self.model, {
            "col": "project_name",
            "clause": "project_equals",
            "value": new_project_name
        })
        if project_already_exists:
            print("Project already exists.")
            return False
        project_id = str(uuid.uuid4())
        created_at = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        project_data = {
            **project_data,
            "id": project_id,
            "created_at": created_at,
            "modifiet_at": created_at
        }
        create_success = self.model.add(params=[tuple(project_data.values())])
        if create_success:
            print(f"Project created with id: {project_id}")
            return project_id
        print("Creating project failed")
        return False

    def create_project_session(self, session_data): 
        project_id = session_data.get("project_id", None) 
        if not project_id:
            print("Project ID not found in the session initiation params")
            return False
        session_id = str(uuid.uuid4())
        # For testing purposes, the session is valid for 365 days
        valid_until = (datetime.today()+ timedelta(days=365)).strftime("%m/%d/%Y, %H:%M:%S")
        session_data = {
            **session_data,
            "session_id": session_id,
            "valid_until": valid_until
        }
        create_success = self.model.add(params=[tuple(session_data.values())])
        if create_success:
            print(f"Session created for project id: {project_id}")
            return session_id
        print(f"Creating project session failed for project id: {project_id}")
        return False
    
    def create_session_participant(self, participant_data):
        session_id = participant_data.get("session_id", None)
        if not session_id:
            print("Session ID not found in session participant params")
            return False
        session_model = self.table_model_factory.get("sessions", None)
        session_exists = self.already_exists(session_model, {
            "col": "session_id",
            "clause": "session_equals",
            "value": session_id
        })
        if not session_exists:
            print(f"Session with id: {session_id} not found")
            return False
        participant_id = str(uuid.uuid4())
        joined_at = datetime.today().strftime("%m/%d/%Y, %H:%M:%S")
        participant_data = {
            **participant_data,
            "participant_id": participant_id,
            "joined_at": joined_at
        }
        create_success = self.model.add(params=[tuple(participant_data.values())])
        if create_success:
            print(f"Session participant: {participant_data} added to session: {session_id}")
            return participant_id
        print(f"Adding session participant failed for session: {session_id}")
        return False



    
    

    
        

    


    
    
        


    



