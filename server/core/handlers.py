from models.projects_model import ProjectsModel
from models.messages_model import MessagesModel
from models.tasks_model import TasksModel
from datetime import datetime, timedelta
import uuid

class ProjectHandler:
    def __init__(self, db):
        self.model = ProjectsModel(db)

    @staticmethod
    def get_all_projects(db):
        return ProjectsModel(db).get({}, all=True)
    
    @staticmethod
    def filter_projects(db, filters, format={}):
        return ProjectsModel(db).get(filters, **format)

    def create_project(self, project_data={}):
        new_project_name = project_data.get("project_name", None)
        if not new_project_name:
            print("No project name found in params")
            return False
        project_already_exists = self.model.already_exists({
            "col": "project_name",
            "clause": "projects_equals",
            "value": new_project_name
        })
        if project_already_exists:
            print("Project name already exists.")
            return False
        timestamp = datetime.now()
        project_data = {
            **project_data,
            "created_at": timestamp,
            "modified_at": timestamp
        }
        project_data = {
            # Order columns to matching model order
            key: project_data[key] for key, type in self.model.columns
        }
        create_success, rows_updated, project_id = self.model.add(
            values=[tuple(project_data.values())], 
            returning="project_id"
            )
        if create_success:
            print(f"Project created with id: {project_id}")
            return project_id
        print("Creating project failed")
        return False

    def delete_projects(self, project_id=None, filters={}):   
        if project_id:
            filters={
                "clauses": [{
                    "col": "project_id", 
                    "clause": "projects_equals", 
                    "value": int(project_id)
                }]
            }
        if not filters:
            print("No filters found for deleting")
            return False
        success, rows_updated,  = self.model.delete(filters)
        if success and rows_updated>0:
            print("Project deleted successfully")
            return True
        print("Deleting project was not successful")
        return False
    
    def update_project(self, project_id, updated_data):
        if not project_id:
            print("Project ID not provided")
            return False
        columns_with_new_values = updated_data.get("columns", None)
        if not columns_with_new_values:
            print("New column-values not provided")
            return False
        success, rows_updated = self.model.update({
            **updated_data,
            "clauses": [{
                "col": "project_id", 
                "clause": "projects_equals", 
                "value": int(project_id)
                }]
            }
        )
        if success and rows_updated==1:
            print(f"Project {project_id} updated successfully")
            return True
        print(f"Project {project_id} was not updated successfully")
        return False

class TaskHandler:
    def __init__(self, db):
        self.model = TasksModel(db)

    @staticmethod
    def get_all_projects(db):
        return TasksModel(db).get({}, all=True)
    
    @staticmethod
    def filter_projects(db, filters, format={}):
        return TasksModel(db).get(filters, **format)
    
class MessageHandler:
    def __init__(self, db):
        self.model = MessagesModel(db)

    @staticmethod
    def get_all_projects(db):
        return MessagesModel(db).get({}, all=True)
    
    @staticmethod
    def filter_projects(db, filters, format={}):
        return MessagesModel(db).get(filters, **format)