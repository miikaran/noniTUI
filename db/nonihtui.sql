--- PostgreSQL environment for the NonihTUI app

-- Table: sessions
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    valid_until DATE
);

-- Table: projects
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    project_name VARCHAR(255),
    description TEXT,
    created_at DATE,
    modified_at TIMESTAMP
);

-- Table: session_participants
CREATE TABLE session_participants (
    participant_id SERIAL PRIMARY KEY,
    session_UUID UUID REFERENCES sessions(session_id),
    participant_name VARCHAR(255),
    joined_at DATE
);

-- Table: messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    project_id INT REFERENCES projects(id),
    session_participant_id INT REFERENCES session_participants(participant_id),
    message_sender VARCHAR(255),
    message_content TEXT,
    message_timestamp TIMESTAMP
);

-- Table: tasks
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    project_id INT REFERENCES projects(id),
    name VARCHAR(255),
    assignee VARCHAR(255),
    description TEXT,
    start_date DATE,
    end_date DATE,
    task_type VARCHAR(10) CHECK (task_type IN ('todo', 'in-progress', 'backlog', 'done')) DEFAULT 'todo'
);

-- Table: tasks_enrichment
CREATE TABLE tasks_enrichment (
    id SERIAL PRIMARY KEY,
    task_id INT REFERENCES tasks(id),
    done_completed SMALLINT,
    updated_tasks_statuses SMALLINT,
    created_tasks SMALLINT,
    tasks_due SMALLINT
);

-- Function: notify_changes_after_insert - Notify connected clients about database changes
CREATE OR REPLACE FUNCTION notify_changes_after_insert()
RETURNS TRIGGER AS
$$
DECLARE
    channel_name TEXT;
BEGIN
    -- Publish inserts on different tables to different named channels
    -- For example:
    --    Changes on projects table -> publish to projects_channel_<project_id>
    --    Changes on messages table -> publish to messages_channel_<project_id>
    --    etc...
    --    Makes it easier to listen and process data from different tables
    channel_name := format('%I_channel_%s', TG_TABLE_NAME, COALESCE(NEW.project_id, 'public'));
    EXECUTE format(
        'NOTIFY %I, %L', 
        format('project_channel_%s', NEW.project_id),
        row_to_json(NEW)::text
    );
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;


-- Trigger: trigger_notify - Execute notifier for each new row to x-table
CREATE TRIGGER trigger_notify_projects
AFTER INSERT
ON projects
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_tasks
AFTER INSERT
ON tasks
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_messages
AFTER INSERT
ON messages
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();