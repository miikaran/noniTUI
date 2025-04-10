-- Trigger: trigger_notify - Execute notifier for each change to x-table

-- TABLE: projects
CREATE TRIGGER trigger_notify_projects_insert
AFTER INSERT
ON projects
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_projects_update
AFTER UPDATE
ON projects
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_projects_delete
AFTER DELETE
ON projects
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

-- TABLE: tasks
CREATE TRIGGER trigger_notify_tasks_insert
AFTER INSERT
ON tasks
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_tasks_update
AFTER UPDATE
ON tasks
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_tasks_delete
AFTER DELETE
ON tasks
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

-- TABLE: messages
CREATE TRIGGER trigger_notify_messages_insert
AFTER INSERT
ON messages
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_messages_update
AFTER UPDATE
ON messages
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_messages_delete
AFTER DELETE
ON messages
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

-- TABLE: session_participants
CREATE TRIGGER trigger_notify_session_participants_insert
AFTER INSERT
ON session_participants
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_session_participants_update
AFTER UPDATE
ON session_participants
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_session_participants_delete
AFTER DELETE
ON session_participants
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();