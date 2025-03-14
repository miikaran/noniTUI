from .models.projects_model import ProjectsModel
from .models.messages_model import MessagesModel
from .models.tasks_model import TasksModel
from datetime import datetime, timedelta
import uuid

class HandlerInterface:
    """Represents a generic interface for handling database requests"""
    def __init__(self, db: object, target_model: object):
        self.db = db
        self.model = target_model(db)
    
    def get_all(self) -> list:
        """Method for getting all data from model"""
        return self.model.select({}, all=True)
    
    def filter_from(self, filters: dict, format: dict={}) -> list:
        """Method to filter data from model with filters"""
        return self.model.select(filters, **format)
    
    @staticmethod
    def get_all(db: object, model: object) -> list:
        return model(db).select({}, all=True)
    
    @staticmethod
    def filter_from(db: object, model: object, filters: dict, format: dict={}) -> list:
        return model(db).select(filters, **format)
    
    def add_record(self, data: list, required_cols: list, unique: dict={}, return_col: str="") -> bool | tuple:
        """General method for adding records to a model

        Args:
            data (list):            List of tuples that presents rows
            required_cols (list):   Keys to require in the record
            unique (dict):          Dictionary containing clauses to check if value already exists
            return_col (str):       Column that we want to return with the insert   

        Returns:
            bool: Boolean value representing success
            tuple: Tuple of success and id if return_col defined        
    
        """
        if not data:
            print(f"Data for {self.model.table} insert not found")
            return False
        for key in required_cols:
            if key not in data:
                print(f"Required {key} not found in new record to {self.model.table}")
                return False
        if unique:
            already_exists = self.model.already_exists(unique)
            if already_exists:
                col = unique.get("col")
                value = unique.get("value")
                print(f"{col} with value {value} already exists in {self.model.table}")
                return False
        ordered_data = self.model.sort_row_values_by_columns(data)
        success, rows_updated, id = self.model.insert(
            values=[tuple(ordered_data.values())], 
            returning=return_col
            )
        if success and id:
            print(f"New record created to {self.model.table} with id: {id}")
            return success, id
        print(f"Failed to add a record to {self.model.table}")
        return False
    
    def update_record(self, id, updated_data: dict, clauses: list) -> bool:
        """General method for updating records in model

        Args:
            id (Optional):          Unique id stored from the record
            updated_data (dict):    Dictionary containing columns, values and clauses for the update
            clauses (list):         List of clauses used to overwrite the ones in updated_data 
            
        Returns:
            bool: Boolean value representing success  

        """
        if not id:
            print(f"{self.model.table} id not provided")
            return False
        columns_with_new_values = updated_data.get("columns", None)
        if not columns_with_new_values:
            print(f"New column-values not provided for update attempt to {self.model.table}")
            return False
        success, rows_updated = self.model.update({
            **updated_data,
            "clauses": clauses
        })
        if success and rows_updated==1:
            print(f"{self.model.table} ID: {id} updated successfully")
            return True
        print(f"{self.model.table} ID: {id} was not updated successfully")
        return False

    def delete_record(self, id=None, filters: dict={}, clauses: dict={}) -> bool:
        """General method for deleting records from model

        Args:
            id (Optional):          Unique id stored from the record
            filters (dict):         Dictionary containing clauses for filtering
            clauses (list):         List of clauses used to overwrite the ones in filters
            
        Returns:
            bool: Boolean value representing success  

        """
        if id:
            if not clauses:
                print(f"No clause found for id specific delete for table {self.model.table}")
                return False
            filters={"clauses": clauses}
        if not filters:
            print("No filters found for deleting")
            return False
        success, rows_updated = self.model.delete(filters)
        if success and rows_updated>0:
            print(f"Row deleted from {self.model.table} successfully")
            return True
        print(f"Deleting with {filters} from {self.model.table} was not successful")
        return False
    
    
class ProjectHandler(HandlerInterface):
    """Represents a handler used to process requests to the projects model"""
    def __init__(self, db: object):
        super().__init__(db=db,target_model=ProjectsModel)
    
    def create_new_project(self, project_data: dict) -> bool | tuple:
        """Method for creating a project, including session.

        Args:
            project_data (dict): New projects data
            
        Returns:
            bool: Boolean value representing success  
            tuple: Tuple of success and created session id

        """
        if not project_data:
            print("No project data provided")
            return False
        project_id = self.add_project(project_data)
        if not project_id:
            return False
        success, session_id = SessionHandler(self.db).create_session({"project_id": project_id})
        if not (success and session_id):
            # Remove the new project if couldn't create a session for it
            deleted = self.delete_projects(project_id=project_id)
            if deleted:
                print(f"Removed project {project_id} for invalid session initialization")
            else: 
                print(f"Session initialization and delete failed for project: {project_id}")
            return False
        # Otherwise -> return the session id for joining
        return True, session_id
        
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
            
    def delete_projects(self, project_id=None, filters={}):   
        """Method for deleting project with id or filters"""
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

class SessionHandler(HandlerInterface):
    """Represents a handler used to handle project sessions"""
    def __init__(self, db):
        super().__init__(db=db, target_model=None)
        # Not sure is this field necessary in the db
        self.valid_until = self.get_valid_until(365)

    def get_valid_until(self, days_from_now, date_format="%m/%d/%Y, %H:%M:%S"):
        """Method for getting datetime object x days in the future"""
        return datetime.today()+timedelta(days=days_from_now).strftime(date_format)
    
    def create_session(self, session_data={}):
        """Method used to create a new session record"""
        return self.add_record(
            data={
                **session_data,
                "session_id": str(uuid.uuid4()),
                "valid_until": self.valid_until
            },
            required_cols=["project_id"],
            return_col="session_id"
        )
    

class TaskHandler(HandlerInterface):
    def __init__(self, db):
        super().__init__(db=db,target_model=TasksModel)

class MessageHandler(HandlerInterface):
    def __init__(self, db):
         super().__init__(db=db,target_model=MessagesModel)
    

    