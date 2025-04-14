CREATE OR REPLACE FUNCTION notify_changes_after_insert()
RETURNS TRIGGER AS
$$
DECLARE
    channel_name TEXT;
    payload TEXT;
    identifier TEXT;
    fetched_project_id TEXT;
BEGIN
    -- Handle DELETE separately using the OLD
    IF TG_OP = 'DELETE' THEN
        BEGIN
            identifier := OLD.project_id::TEXT;
        EXCEPTION WHEN undefined_column OR others THEN
            BEGIN
                SELECT project_id::TEXT INTO fetched_project_id
                FROM sessions
                WHERE session_id = OLD.session_UUID;

                identifier := COALESCE(fetched_project_id, OLD.session_UUID::TEXT, 'public');
            EXCEPTION WHEN OTHERS THEN
                identifier := COALESCE(OLD.session_UUID::TEXT, 'public');
            END;
        END;
    ELSE
        BEGIN
            identifier := NEW.project_id::TEXT;
        EXCEPTION WHEN undefined_column OR others THEN
            BEGIN
                SELECT project_id::TEXT INTO fetched_project_id
                FROM sessions
                WHERE session_id = NEW.session_UUID;

                identifier := COALESCE(fetched_project_id, NEW.session_UUID::TEXT, 'public');
            EXCEPTION WHEN OTHERS THEN
                identifier := COALESCE(NEW.session_UUID::TEXT, 'public');
            END;
        END;
    END IF;

    channel_name := format('%I_channel_%s', TG_TABLE_NAME, identifier);

    IF TG_OP = 'INSERT' THEN
        payload := json_build_object('operation', 'INSERT', 'table', TG_TABLE_NAME, 'new_data', row_to_json(NEW))::text;
    ELSIF TG_OP = 'UPDATE' THEN
        payload := json_build_object('operation', 'UPDATE', 'table', TG_TABLE_NAME, 'updated_data', row_to_json(NEW))::text;
    ELSIF TG_OP = 'DELETE' THEN
        payload := json_build_object('operation', 'DELETE', 'table', TG_TABLE_NAME, 'old_data', row_to_json(OLD))::text;
    END IF;

    RAISE NOTICE 'Notifying on channel: %, payload: %', channel_name, payload;

    EXECUTE format(
        'NOTIFY %I, %L', 
        channel_name,
        payload
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;
