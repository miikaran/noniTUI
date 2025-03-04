-- Trigger: trigger_notify - Execute notifier for each change to x-table

-- TABLE: projects
CREATE TRIGGER trigger_notify_projects
AFTER INSERT
ON projects
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_projects
AFTER UPDATE
ON projects
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_projects
AFTER DELETE
ON projects
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

-- TABLE: tasks
CREATE TRIGGER trigger_notify_tasks
AFTER INSERT
ON tasks
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_tasks
AFTER UPDATE
ON tasks
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_tasks
AFTER DELETE
ON tasks
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

-- TABLE: messages
CREATE TRIGGER trigger_notify_messages
AFTER INSERT
ON messages
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_messages
AFTER UPDATE
ON messages
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();

CREATE TRIGGER trigger_notify_messages
AFTER DELETE
ON messages
FOR EACH ROW
EXECUTE PROCEDURE notify_changes_after_insert();