from .models.projects_model import ProjectsModel
from .models.messages_model import MessagesModel
from .models.tasks_model import TasksModel
from .models.sessions_model import SessionsModel, SessionParticipantsModel
from datetime import datetime, timedelta
import uuid
from core.utils.exceptions import BadRequestException, NotFoundException, ConflictException, InternalServerException, NoniAPIException, UnauthorizedException

class HandlerInterface:
    """Represents a generic interface for handling API requests for database stuff"""
    def __init__(self, db: object, target_model: object):
        self.db = db
        self.model = target_model(db)
    
    def _get_all(self) -> list:
        """Method for getting all data from model"""
        return self.model.select({}, all=True)
    
    def _filter_from(self, filters: list, format: dict={}) -> list:
        """Method to filter data from model with filters"""
        return self.model.select(filters, **format)
    
    @staticmethod
    def get_all(db: object, model: object) -> list:
        return model(db).select({}, all=True)
    
    @staticmethod
    def filter_from(db: object, model: object, filters: list, format: dict={}) -> list:
        return model(db).select(filters, **format)
    
    def add_record(self, data: dict, required_cols: list, unique: dict={}, return_col: str="") -> bool | tuple:
        """General method for adding records to a model"""
        if not data:
            print(f"Data for {self.model.table} insert not found")
            raise BadRequestException("No data provided for insertion")
        for key in required_cols:
            if key not in data:
                print(f"Required {key} not found in new record to {self.model.table}")
                raise BadRequestException(f"Required key '{key}' not found in record")
        if unique:
            already_exists = self.model.already_exists(unique)
            if already_exists:
                col = unique.get("col")
                value = unique.get("value")
                print(f"{col} with value {value} already exists in {self.model.table}")
                raise ConflictException(f"Record already exists: {col} -> {value}")
        ordered_data = self.model.sort_row_values_by_columns(data)
        success, rows_updated, id = self.model.insert(
            values=[tuple(ordered_data.values())], 
            returning=return_col
            )
        if success and id:
            print(f"New record created to {self.model.table} with id: {id}")
            return success, id
        print(f"Failed to add a record to {self.model.table}")
        raise InternalServerException(f"Failed to insert record into {self.model.table}")

    def update_record(self, id, updated_data: dict, clauses: list) -> bool:
        """General method for updating records in model"""
        if not id:
            print(f"{self.model.table} id not provided")
            raise BadRequestException("Unique ID of updated record not found")
        columns_with_new_values = updated_data.get("columns", None)
        if not columns_with_new_values:
            print(f"New column-values not provided for update attempt to {self.model.table}")
            raise BadRequestException("No values provided for update")
        success, rows_updated = self.model.update({
            **updated_data,
            "clauses": clauses
        })
        if success and rows_updated==1:
            print(f"{self.model.table} ID: {id} updated successfully")
            return True
        print(f"{self.model.table} ID: {id} was not updated successfully")
        raise InternalServerException(f"Failed to update record with ID {id} in {self.model.table}")

    def delete_record(self, id=None, filters: dict={}, clauses: dict={}) -> bool:
        """General method for deleting records from model"""
        if id:
            if not clauses:
                print(f"No clause found for id specific delete for table {self.model.table}")
                raise BadRequestException("Missing clauses for ID-based deletion")
            filters={"clauses": clauses}
        if not filters:
            print("No filters found for deleting")
            raise BadRequestException("No filters provided for deletion")
        success, rows_updated = self.model.delete(filters)
        if success and rows_updated>0:
            print(f"Row deleted from {self.model.table} successfully")
            return True
        print(f"Deleting with {filters} from {self.model.table} was not successful")
        raise NotFoundException(f"Record not found for deletion in {self.model.table}")

class ProjectHandler(HandlerInterface):
    """Represents a handler used to process requests to the projects model"""
    def __init__(self, db: object):
        super().__init__(db=db,target_model=ProjectsModel)
    
    def create_new_project(self, project_data: dict) -> bool | tuple:
        """Method for creating a project, including session"""
        success, project_id = self.add_project(project_data)
        if not (success and project_id):
            raise InternalServerException("Failed to create a new project")
        success, session_id = SessionHandler(self.db).create_session({"project_id": project_id})
        if not (success and session_id):
            # Remove the new project if couldn't create a session for it
            deleted = self.delete_projects(project_id=project_id)
            if deleted:
                print(f"Removed project {project_id} for invalid session initialization")
            else: 
                print(f"Session initialization and delete failed for project: {project_id}")
                raise InternalServerException(f"Rollback for project: {project_id} failed after failed session init")
            raise InternalServerException("Failed to create a new project")
        # Otherwise -> return the session id & project_id for joining
        return session_id, project_id
            
    def add_project(self, project_data={}):
        """Method for adding new project record"""
        timestamp = datetime.now()
        return self.add_record(
            data={
                **project_data,
                "created_at": timestamp,
                "modified_at": timestamp
            },
            required_cols=["project_name"],
            unique={
                "col": "project_name",
                "clause": "projects_equals",
                "value": project_data.get("project_name", None)
            },
            return_col="project_id"
        )
            
    def delete_projects(self, project_id=None, filters={}, session_id=None):   
        """Method for deleting project with id or filters"""
        if session_id and project_id:
            is_valid = SessionHandler(self.db).is_valid_session(session_id=session_id)
            if not is_valid:
                raise InternalServerException("Invalid session for deleting projects")
        return self.delete_record(
            id=project_id,
            filters=filters,
            clauses=[{
                "col": "project_id", 
                "clause": "projects_equals", 
                "value": int(project_id)
            }]
        )
    
    def update_project(self, project_id, updated_data):
        """Method for updating specific projects"""
        return self.update_record(
            id=project_id,
            updated_data=updated_data,
            clauses=[{
                "col": "project_id", 
                "clause": "projects_equals", 
                "value": project_id
            }]
        )

    def join_project(self, session_id, username):
        """Method for joining projects current session aka adding user as session participant"""
        session_participant_handler = SessionParticipantHandler(self.db)
        participant_id = session_participant_handler.add_session_participant(session_id, username)
        return participant_id

class SessionHandler(HandlerInterface):
    """Represents a handler used to handle project sessions"""
    SESSION_COOKIE_NAME = "session_id"
    SESSION_EXPIRATION_DAYS = 365
    SESSION_EXPIRATION_SECONDS = SESSION_EXPIRATION_DAYS * 24 * 60 * 60

    def __init__(self, db):
        super().__init__(db=db, target_model=SessionsModel)
        # Not sure is this field necessary in the db
        self.valid_until = self.get_valid_until(self.SESSION_EXPIRATION_DAYS)
    
    async def check_request_session(self, request=None):
        """Check session validity from request cookies"""
        session_id = request.cookies.get(self.SESSION_COOKIE_NAME)
        if not session_id:
            raise UnauthorizedException()
        is_valid_session = self.is_valid_session(session_id=session_id)
        if not is_valid_session:
            raise NoniAPIException(status_code=403, detail="Session expired or invalid")
        return session_id

    def get_session(self, session_id):
        """Get session with session id"""
        if not session_id:
            raise BadRequestException("No session id provided")
        return self._filter_from(
            filters=[{
                "col": "session_id",
                "clause": "sessions_equals",
                "value": str(session_id)
            }]
        )
    
    def get_valid_until(self, days_from_now, date_format="%m/%d/%Y, %H:%M:%S"):
        """Method for getting datetime object x days in the future as a formatted string"""
        return datetime.today() + timedelta(days=days_from_now)
    
    def create_session(self, session_data={}):
        """Method used to create a new session record"""
        session_id = self.add_record(
            data={
                **session_data,
                "session_id": str(uuid.uuid4()),
                "valid_until": self.valid_until
            },
            required_cols=["project_id"],
            return_col="session_id"
        )
        if not session_id:
            raise InternalServerException("Could not create a session")
        return session_id

    def is_valid_session(self, session_id=None, project_id=None):
        """Check if valid session by session_id or project_id"""
        target_col = None
        target_value = session_id or project_id
        if session_id:
            target_col = "session_id"
        elif project_id:
            target_col = "project_id"
        if target_col and target_value:
            session_data = self._filter_from(
                [{
                    "col": target_col, 
                    "clause": "sessions_equals", 
                    "value": target_value
                }]
            )
            if not len(session_data) > 0:
                raise NotFoundException(f"{target_col}:{target_value} not found in sessions")
            valid_until = session_data[0]["valid_until"]
            if valid_until > datetime.now().date():
                return True, valid_until
            raise NoniAPIException(
                status_code=403,
                detail="Session expired or invalid"
            )
        raise BadRequestException("Session ID or Project ID not found for querying session")

class SessionParticipantHandler(HandlerInterface):
    def __init__(self, db):
        super().__init__(db=db, target_model=SessionParticipantsModel)

    def get_session_participants(self, session_id):
        """Get session participants with session id"""
        if not session_id:
            raise BadRequestException("No session id provided")
        return self._filter_from(
            filters=[{
                "col": "session_uuid",
                "clause": "session_participant_equals",
                "value": str(session_id)
            }]
        )
    
    def is_participant_in_session(self, session_id, participant_id):
        """Check whether participant is in a session"""
        participant_ids = [
            row["participant_id"] 
            for row in self.get_session_participants(session_id)
            ]
        if len(participant_ids) < 1:
            return False
        if participant_id in participant_ids:
            return True
        return False
    
    def get_session_participants_by_project_id(self, project_id):
        """Get session participants by the project id"""
        if not project_id:
            raise BadRequestException("No project id provided")          
        sessions_for_project = SessionHandler(self.db)._filter_from(
            filters=[{
                "col": "project_id", 
                "clause": "sessions_equals", 
                "value": int(project_id)
                }]
        )
        if len(sessions_for_project) > 0:
            session_ids = tuple([row["session_id"] for row in sessions_for_project])
            for id in session_ids:
                return self._filter_from(
                    filters=[{
                        "col": "session_uuid",
                        "clause": "session_participant_equals_in",
                        "value": session_ids,
                        "operator": " AND "
                    }]
                )  
        raise NotFoundException(f"Sessions not found for project_id: {project_id}")

    def add_session_participant(self, session_id, username):
        """Add new session participant to a existing session"""
        if not (session_id and username):
            raise BadRequestException("Session ID or Username not found for joining project")
        success, participant_id = self.add_record(
            data={
                "session_uuid": str(session_id), 
                "participant_name": username,
                "joined_at": datetime.now()
            },
            required_cols=["session_uuid", "participant_name", "joined_at"],
            return_col="participant_id"
            )
        if not (success and participant_id):
            raise InternalServerException(f"Failed to add a session participant to session: {session_id}")
        return participant_id

class TaskHandler(HandlerInterface):
    def __init__(self, db):
        super().__init__(db=db,target_model=TasksModel)

    def get_project_tasks(self, project_id):
        """Get tasks for project"""
        if not project_id:
            raise BadRequestException("Project ID not provided")
        return self._filter_from(
            filters=[{
                "col": "project_id",
                "clause": "tasks_equals",
                "value": int(project_id)
            }]
        )

    def add_task_to_project(self, task_data, session_id):
        """Add new task to project"""
        if not (task_data and session_id):
            raise BadRequestException("Task data or session id not found ")
        session_handler = SessionHandler(self.db)
        session_data = session_handler.get_session(session_id)
        project_id = session_data[0]["project_id"]
        if not project_id:
            raise NotFoundException(f"Project not found for session id: {session_id}")
        timestamp = datetime.now()
        success, task_id = self.add_record(
            data={
                **task_data,
                "project_id": int(project_id), 
                "added_at": timestamp,
                "start_date": datetime.fromisoformat((task_data["start_date"])),
                "end_date": datetime.fromisoformat((task_data["end_date"]))
            },
            required_cols=["project_id", "name", "assignee", "task_type"],
            return_col="id"
            )
        if not success:
            raise InternalServerException(f"Failed to create task for project: {project_id}. ID not returned")
        return task_id

    def update_project_task(self, task_data, task_id):
        """Update task in project"""
        if not (task_data and task_id):
            raise BadRequestException("Task data or task id not found ")    
        project_id = task_data["project_id"]
        success = self.update_record(
            id=task_id,
            updated_data={
                "columns": {
                    **task_data,
                    "project_id": int(project_id),
                } 
            },
            clauses=[{
                "col": "id",
                "clause": "tasks_equals",
                "value": int(task_id)
            }]
            )
        if not success:
            raise InternalServerException(f"Failed to update task {task_id} for project: {project_id}")
        return task_id

    def delete_task_from_project(self, task_id, session_id):
        """Delete task from project"""
        if not (task_id and session_id):
            raise BadRequestException("Task data not found ")
        session_handler = SessionHandler(self.db)
        session_data = session_handler.get_session(session_id)
        project_id = session_data[0]["project_id"]
        success = self.delete_record(
            id=task_id,
            clauses=[{"col": "id", "clause": "tasks_equals", "value": int(task_id)}]
        )
        if not success:
            raise InternalServerException(f"Failed to delete task {task_id} from project: {project_id}")
        return task_id

class MessageHandler(HandlerInterface):
    def __init__(self, db):
         super().__init__(db=db,target_model=MessagesModel)
    

    