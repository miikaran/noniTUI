-- Function: notify_changes_after_insert - Notify connected clients about database changes
CREATE OR REPLACE FUNCTION notify_changes_after_insert()
RETURNS TRIGGER AS
$$
DECLARE
    channel_name TEXT;
    payload TEXT;
BEGIN
    -- Publish updates on different tables to different named channels
    -- For example:
    --    Changes on projects table -> publish to projects_channel_<project_id>
    --    Changes on messages table -> publish to messages_channel_<project_id>
    --    etc...
    --    Makes it easier to listen and process data from different tables
    channel_name := format('%I_channel_%s', TG_TABLE_NAME, COALESCE(NEW.project_id::TEXT, 'public'));
    IF TG_OP = 'INSERT' THEN
        payload := json_build_object('operation', 'INSERT', 'table', TG_TABLE_NAME, 'new_data', row_to_json(NEW))::text;
    ELSIF TG_OP = 'UPDATE' THEN
        payload := json_build_object('operation', 'UPDATE', 'table', TG_TABLE_NAME, 'updated_data', row_to_json(NEW))::text;
    ELSIF TG_OP = 'DELETE' THEN
        payload := json_build_object('operation', 'DELETE', 'table', TG_TABLE_NAME, 'old_data', row_to_json(OLD))::text;
    END IF;
    -- Send updated data to project specific channel
    EXECUTE format(
        'NOTIFY %I, %L', 
        channel_name,
        payload
    );
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;