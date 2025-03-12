from fastapi import FastAPI
from models.projects_model import ProjectsModel
from psycopg2 import connect
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

POSTGRE_USERNAME=os.getenv('POSTGRE_USERNAME')
POSTGRE_PASSWORD=os.getenv('POSTGRE_PASSWORD')
POSTGRE_HOST=os.getenv('POSTGRE_HOST')
POSTGRE_PORT=os.getenv('POSTGRE_PORT')
POSTGRE_DATABASE=os.getenv('POSTGRE_DATABASE')

app = FastAPI(
    title="NoniAPI",
    debug=True
)

@app.get("/")
async def root():
    sql = ProjectsModel(
        connect(
            database=POSTGRE_DATABASE,
            user=POSTGRE_USERNAME,
            password=POSTGRE_PASSWORD,
            host=POSTGRE_HOST,
            port=POSTGRE_PORT
        )
    )
    print(sql.get(params=[
        {
            "col": "project_id",
            "clause": "projects_equals",
            "value": 1
        }
    ]))

if __name__ == "__main__":
    uvicorn.run(
        app="main:app", 
        host="localhost", 
        port=8000,
        reload=True
    )