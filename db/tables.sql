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