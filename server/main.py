from fastapi import FastAPI
import uvicorn
from api import projects, messages, tasks

"""
If the debug is on, the errors raised during handling will be returned to client by FastAPI by default,
and the centralized_error_handler won't work. If it is set to False, then it should handle exceptions properly
"""
app = FastAPI(
    title="NoniAPI",
    debug=False
)

app.include_router(projects.router)
app.include_router(messages.router)
app.include_router(tasks.router)

@app.get("/")
async def root():
    return {"message": "This is the root of NoniAPI"}

if __name__ == "__main__":
    uvicorn.run(
        app="main:app", 
        host="localhost", 
        port=8000,
        reload=True
    )