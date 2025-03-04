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