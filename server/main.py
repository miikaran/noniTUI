from fastapi import FastAPI, HTTPException
import uvicorn
from request_handlers import Factories

app = FastAPI(
    title="NoniAPI",
    debug=True
)

@app.get("/")
async def root():
    handler = Factories.request_handler_factory(
        request_type="database_update",
        params={
            "statement_params": [{
                "col": "project_id",
                "clause": "projects_equals",
                "value": 1
            }],
            "target_table": "projects",
            "modification_type": "select",
        }
    )
    print(handler.handle_request())
    return {}

if __name__ == "__main__":
    uvicorn.run(
        app="main:app", 
        host="localhost", 
        port=8000,
        reload=True
    )