# Ohjeet nyypälle

## Database stuff
1. Make sure PostgreSQL is installed
2. Run the setup.sh in environment/ to setup the sql stuff. I think it requires sudo.
3. If it didn't output any errors, check that all of the tables are in PostgreSQL
4. Change credentials from environment/.env.development if required

## Python stuff
1. Install pip packages from requirements.txt
2. Run **fastapi dev main.py** to start the server. If no errors -> guud.

## API stuff

Next, we will test
- creating project
- joining it
- adding tasks to it
- updating tasks in it
- deleting tasks in it
- (message routet viel puuttuu)

with curl

#### 1. Creating project

New project schema in /api/projects

This will initialize new project in db, and create a session for it.
It returns the session_id, that will be used to join the project session

curl -X POST -H "Content-Type: application/json" -d '{"project_name": "miikanprojekti", "description": "joku taski desci"}' http://localhost:8000/projects/

#### 2. Join project

Join the project by adding the returned session_id to the join route, and also a username query param, the user wants to identify with in the session.

This will add user as session participant to the project session.
It returns a session_participant_id.

curl -X POST  http://localhost:8000/projects/join/30ca08c4-bb0a-419e-a7e5-3c85cd9e67c8?username=Miika

#### 3. Add tasks to project

New task schema in /api/tasks

Give the session id as cookie (curl does not store cookies anywhere, so thats why we have to give it manually here, en tiiä mite toi menee textualizes). 

This adds a new task to the project that is identified with the session_id.
Returns task_id

curl -X POST --cookie "session_id=30ca08c4-bb0a-419e-a7e5-3c85cd9e67c8" -H "Content-Type: application/json" -d '{"name": "uusi taski", "assignee": "miika", "description": "ju", "start_date": "2025-04-09", "end_date": "2025-04-28", "task_type": "todo"}' http://localhost:8000/tasks/new

#### 4. Update tasks in project

Add the task id you want to modify to the URL
Give the session id as cookie again, and the updated task data as body.

This will replace the whole task with the updated data.
Returns task_id that was modified

curl -X PUT --cookie "session_id=30ca08c4-bb0a-419e-a7e5-3c85cd9e67c8" -H "Content-Type: application/json" -d '{"name": "miikan taski paivitys", "assignee": "miika", "description": "ju", "start_date": "2025-04-08", "end_date": "2025-04-28", "task_type": "todo"}' http://localhost:8000/tasks/12

#### 5. Delete tasks in project

To delete task, add the task id to the URL and include session_id.
This will delete the task from the project.
Returns the task_id that was removed

curl -X DELETE --cookie "session_id=30ca08c4-bb0a-419e-a7e5-3c85cd9e67c8" http://localhost:8000/tasks/12


### Websocket / Notifier stuff

tähän pitää lisää viel noi reaaliaikais hommat, et miten ne toimii













