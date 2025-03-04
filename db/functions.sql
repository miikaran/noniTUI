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