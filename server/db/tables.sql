--- PostgreSQL tables for the NonihTUI app

-- Table: projects
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at DATE NOT NULL,
    modified_at TIMESTAMP NOT NULL
);

-- Table: sessions
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    project_id INT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    valid_until DATE NOT NULL
);

-- Table: session_participants
CREATE TABLE session_participants (
    participant_id SERIAL PRIMARY KEY,
    session_UUID UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    participant_name VARCHAR(255) NOT NULL,
    joined_at DATE NOT NULL
);

-- Table: messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    project_id INT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    session_participant_id INT NOT NULL REFERENCES session_participants(participant_id) ON DELETE CASCADE,
    message_sender VARCHAR(255) NOT NULL,
    message_content TEXT NOT NULL,
    message_timestamp TIMESTAMP NOT NULL
);

-- Table: tasks
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    project_id INT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    assignee VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    task_type VARCHAR(10) NOT NULL CHECK (task_type IN ('todo', 'in-progress', 'backlog', 'done')) DEFAULT 'todo'
);

-- Table: tasks_enrichment
CREATE TABLE tasks_enrichment (
    id SERIAL PRIMARY KEY,
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    done_completed SMALLINT NOT NULL,
    updated_tasks_statuses SMALLINT NOT NULL,
    created_tasks SMALLINT NOT NULL,
    tasks_due SMALLINT NOT NULL
);
