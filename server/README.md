# ohjeet nyypälle
---

## DB stuff

1. Ensure PostgreSQL is installed and running.
2. Navigate to the `environment/` directory and run the setup script:

   ```bash
   sudo ./setup.sh
   ```

3. If the script completes without errors, verify that all required tables have been created in your PostgreSQL database.
4. If needed, update database credentials in `environment/.env.development`.

---

## Python stuff

1. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI dev server:

   ```bash
   fastapi dev main.py
   ```

3. If no errors occur, guud.

---

## API examples w curl

- Creating a project
- Joining a session
- Getting tasks
- Adding tasks
- Updating tasks
- Deleting tasks
- (Message routes need to badded)

---

### 1. Creating project

New project schema is defined in `/api/projects`.

This will initialize a new project and a session for it in the database, and return a `session_id`, which is used for joining it.

Sets a cookie in the response and returns `session_id`

```bash
curl -X POST -H "Content-Type: application/json" -d '{"project_name": "miikanprojekti", "description": "joku taski desci"}' http://localhost:8000/projects/
```

---

### 2. Join project

Join the project with the `session_id` received, and providing a `username` as a query param

Returns a `session_participant_id`.

```bash
curl -X POST  http://localhost:8000/projects/join/30ca08c4-bb0a-419e-a7e5-3c85cd9e67c8?username=Miika
```

---

### 3. Get project tasks

Get tasks within a project, with the project's `session id`

Returns list of tasks in the target project

```bash
curl --cookie "session_id=30ca08c4-bb0a-419e-a7e5-3c85cd9e67c8" http://localhost:8000/tasks/
```

### 4. Add tasks to project

New task schema is defined in `/api/tasks`.

Make sure youu provide the `session_id` as a cookie. (curl does not store cookies automatically, so you must include it manually. En tiiä miten tä toimii textualizes, et käsitteleeks se cookiet miten)

Returns a `task_id`.

```bash
curl -X POST --cookie "session_id=30ca08c4-bb0a-419e-a7e5-3c85cd9e67c8" -H "Content-Type: application/json" -d '{"name": "uusi taski", "assignee": "miika", "description": "ju", "start_date": "2025-04-09", "end_date": "2025-04-28", "task_type": "todo"}' http://localhost:8000/tasks/new
```

---

### 5. Update tasks in project

Use target `task_id` to update in the URL, the updated data in the body, and the `session_id` as a cookie.

Replaces the task with the new data and returns the `task_id` that was updated.

```bash
curl -X PUT --cookie "session_id=30ca08c4-bb0a-419e-a7e5-3c85cd9e67c8" -H "Content-Type: application/json" -d '{"name": "miikan taski paivitys", "assignee": "miika", "description": "ju", "start_date": "2025-04-08", "end_date": "2025-04-28", "task_type": "todo"}' http://localhost:8000/tasks/12
```

---

### 6. Delete tasks in project

Add the target `task_id` again in the URL and provide the `session_id` as a cookie.

Returns the deleted `task_id`.

```bash
curl -X DELETE --cookie "session_id=30ca08c4-bb0a-419e-a7e5-3c85cd9e67c8" http://localhost:8000/tasks/12
```

---

## Websocket / notifier stuff

lisään tän myöhemmi
