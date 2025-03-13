from fastapi import FastAPI
import uvicorn
from request_handlers import AppDatabaseHandler
from exceptions import NoniAPIException
from dotenv import load_dotenv
import os

load_dotenv()

postgresql_credentials = {
    "user": os.getenv('POSTGRE_USERNAME'),
    "password": os.getenv('POSTGRE_PASSWORD'),
    "host": os.getenv('POSTGRE_HOST'),
    "port": os.getenv('POSTGRE_PORT'),
    "database": os.getenv('POSTGRE_DATABASE')
}

app = FastAPI(
    title="NoniAPI",
    debug=True
)

@app.get("/")
async def root():
    request_handler = AppDatabaseHandler(
        "projects",
        postgresql_credentials,
        NoniAPIException
    )
    print(request_handler.get_projects([{
                "col": "project_id",
                "clause": "projects_equals",
                "value": 1
            }]))

if __name__ == "__main__":
    uvicorn.run(
        app="main:app", 
        host="localhost", 
        port=8000,
        reload=True
    )