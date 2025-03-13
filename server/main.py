from fastapi import FastAPI
import uvicorn
from api import projects, messages, tasks

app = FastAPI(
    title="NoniAPI",
    debug=True
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