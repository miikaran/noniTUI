--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'LATIN1';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:VHJPYW/aWHOTmfKD8IPJng==$ijtcJutUVJ/vFWvaMcLjTMDrc3MkV0x3EKoiqX0V97A=:f9eTda74F+M5RRKFxezymWwJ8TAbioYqC5WFfRKbTgk=';
CREATE ROLE vboxuser;
ALTER ROLE vboxuser WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:RwJBCy+TJr09kCgErg4EHw==$nh8mwSFRnPulS3kBiQi7Naxa9Oh825+tmhOsM+gTzuU=:Wh4nbO7bmsElcj1lgt+PfRBzOvEeEwDVnei3ekJBX0o=';

--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'LATIN1';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

--
-- Database "nonidb" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'LATIN1';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: nonidb; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE nonidb WITH TEMPLATE = template0 ENCODING = 'LATIN1' LOCALE = 'en_US';


ALTER DATABASE nonidb OWNER TO postgres;

\connect nonidb

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'LATIN1';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: notify_changes_after_insert(); Type: FUNCTION; Schema: public; Owner: vboxuser
--

CREATE FUNCTION public.notify_changes_after_insert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.notify_changes_after_insert() OWNER TO vboxuser;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: vboxuser
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    project_id integer,
    session_participant_id integer,
    message_sender character varying(255),
    message_content text,
    message_timestamp bigint
);


ALTER TABLE public.messages OWNER TO vboxuser;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: vboxuser
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO vboxuser;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vboxuser
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: vboxuser
--

CREATE TABLE public.projects (
    project_id integer NOT NULL,
    project_name character varying(255),
    -- No need, for now.
    -- description text,
    created_at date,
    modified_at timestamp without time zone
);


ALTER TABLE public.projects OWNER TO vboxuser;

--
-- Name: projects_project_id_seq; Type: SEQUENCE; Schema: public; Owner: vboxuser
--

CREATE SEQUENCE public.projects_project_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.projects_project_id_seq OWNER TO vboxuser;

--
-- Name: projects_project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vboxuser
--

ALTER SEQUENCE public.projects_project_id_seq OWNED BY public.projects.project_id;


--
-- Name: session_participants; Type: TABLE; Schema: public; Owner: vboxuser
--

CREATE TABLE public.session_participants (
    participant_id integer NOT NULL,
    session_uuid uuid,
    participant_name character varying(255),
    joined_at timestamp without time zone
);


ALTER TABLE public.session_participants OWNER TO vboxuser;

--
-- Name: session_participants_participant_id_seq; Type: SEQUENCE; Schema: public; Owner: vboxuser
--

CREATE SEQUENCE public.session_participants_participant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.session_participants_participant_id_seq OWNER TO vboxuser;

--
-- Name: session_participants_participant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vboxuser
--

ALTER SEQUENCE public.session_participants_participant_id_seq OWNED BY public.session_participants.participant_id;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: vboxuser
--

CREATE TABLE public.sessions (
    session_id uuid NOT NULL,
    project_id integer,
    valid_until date
);


ALTER TABLE public.sessions OWNER TO vboxuser;

--
-- Name: tasks; Type: TABLE; Schema: public; Owner: vboxuser
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    project_id integer,
    name character varying(255),
    assignee character varying(255),
    description text,
    start_date date,
    end_date date,
    task_type character varying(20) DEFAULT 'todo'::character varying,
    added_at timestamp without time zone,
    CONSTRAINT tasks_task_type_check CHECK (((task_type)::text = ANY (ARRAY[('todo'::character varying)::text, ('in-progress'::character varying)::text, ('backlog'::character varying)::text, ('done'::character varying)::text])))
);


ALTER TABLE public.tasks OWNER TO vboxuser;

--
-- Name: tasks_enrichment; Type: TABLE; Schema: public; Owner: vboxuser
--

CREATE TABLE public.tasks_enrichment (
    id integer NOT NULL,
    task_id integer,
    done_completed smallint,
    updated_tasks_statuses smallint,
    created_tasks smallint,
    tasks_due smallint
);


ALTER TABLE public.tasks_enrichment OWNER TO vboxuser;

--
-- Name: tasks_enrichment_id_seq; Type: SEQUENCE; Schema: public; Owner: vboxuser
--

CREATE SEQUENCE public.tasks_enrichment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tasks_enrichment_id_seq OWNER TO vboxuser;

--
-- Name: tasks_enrichment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vboxuser
--

ALTER SEQUENCE public.tasks_enrichment_id_seq OWNED BY public.tasks_enrichment.id;


--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: vboxuser
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tasks_id_seq OWNER TO vboxuser;

--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vboxuser
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: projects project_id; Type: DEFAULT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.projects ALTER COLUMN project_id SET DEFAULT nextval('public.projects_project_id_seq'::regclass);


--
-- Name: session_participants participant_id; Type: DEFAULT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.session_participants ALTER COLUMN participant_id SET DEFAULT nextval('public.session_participants_participant_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: tasks_enrichment id; Type: DEFAULT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.tasks_enrichment ALTER COLUMN id SET DEFAULT nextval('public.tasks_enrichment_id_seq'::regclass);


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: vboxuser
--

COPY public.messages (id, project_id, session_participant_id, message_sender, message_content, message_timestamp) FROM stdin;
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: vboxuser
--

COPY public.projects (project_id, project_name, description, created_at, modified_at) FROM stdin;
60	miikanprojekti	miikanprojekti ddeskriptioni	2025-04-04	2025-04-04 23:25:07.216459
61	miikanprojekti2	miikanprojekti ddeskriptioni	2025-04-05	2025-04-05 01:05:06.816844
\.


--
-- Data for Name: session_participants; Type: TABLE DATA; Schema: public; Owner: vboxuser
--

COPY public.session_participants (participant_id, session_uuid, participant_name, joined_at) FROM stdin;
12	2324969c-2a36-45b2-9059-0d76871554a5	Miika	2025-04-04 23:25:24.511007
13	2324969c-2a36-45b2-9059-0d76871554a5	Miika	2025-04-04 23:29:04.629505
14	9efeab2a-f195-442b-8ceb-809350751cc1	Miikulii	2025-04-05 01:07:34.84006
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: vboxuser
--

COPY public.sessions (session_id, project_id, valid_until) FROM stdin;
2324969c-2a36-45b2-9059-0d76871554a5	60	2026-04-04
9efeab2a-f195-442b-8ceb-809350751cc1	61	2026-04-05
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: vboxuser
--

COPY public.tasks (id, project_id, name, assignee, description, start_date, end_date, task_type, added_at) FROM stdin;
3	60	UI suunittelu lis�ys	MIika	t�ss� taskissa lis�t��n jotain uihin	2025-04-07	2025-04-20	todo	2025-04-07 14:19:04.247732
5	60	UI suunittelu lis�ys uusin	MIika	t�ss� taskissa lis�t��n jotain uihin	2025-04-07	2025-04-20	todo	2025-04-07 14:37:02.380715
6	60	UI suunittelu lis�ys uusin	MIika	t�ss� taskissa lis�t��n jotain uihin	2025-04-07	2025-04-20	todo	2025-04-07 14:37:16.510065
\.


--
-- Data for Name: tasks_enrichment; Type: TABLE DATA; Schema: public; Owner: vboxuser
--

COPY public.tasks_enrichment (id, task_id, done_completed, updated_tasks_statuses, created_tasks, tasks_due) FROM stdin;
\.


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vboxuser
--

SELECT pg_catalog.setval('public.messages_id_seq', 1, false);


--
-- Name: projects_project_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vboxuser
--

SELECT pg_catalog.setval('public.projects_project_id_seq', 61, true);


--
-- Name: session_participants_participant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vboxuser
--

SELECT pg_catalog.setval('public.session_participants_participant_id_seq', 14, true);


--
-- Name: tasks_enrichment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vboxuser
--

SELECT pg_catalog.setval('public.tasks_enrichment_id_seq', 1, false);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vboxuser
--

SELECT pg_catalog.setval('public.tasks_id_seq', 6, true);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (project_id);


--
-- Name: session_participants session_participants_pkey; Type: CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.session_participants
    ADD CONSTRAINT session_participants_pkey PRIMARY KEY (participant_id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (session_id);


--
-- Name: tasks_enrichment tasks_enrichment_pkey; Type: CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.tasks_enrichment
    ADD CONSTRAINT tasks_enrichment_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: messages trigger_notify_messages_delete; Type: TRIGGER; Schema: public; Owner: vboxuser
--

CREATE TRIGGER trigger_notify_messages_delete AFTER DELETE ON public.messages FOR EACH ROW EXECUTE FUNCTION public.notify_changes_after_insert();


--
-- Name: messages trigger_notify_messages_insert; Type: TRIGGER; Schema: public; Owner: vboxuser
--

CREATE TRIGGER trigger_notify_messages_insert AFTER INSERT ON public.messages FOR EACH ROW EXECUTE FUNCTION public.notify_changes_after_insert();


--
-- Name: messages trigger_notify_messages_update; Type: TRIGGER; Schema: public; Owner: vboxuser
--

CREATE TRIGGER trigger_notify_messages_update AFTER UPDATE ON public.messages FOR EACH ROW EXECUTE FUNCTION public.notify_changes_after_insert();


--
-- Name: projects trigger_notify_projects_delete; Type: TRIGGER; Schema: public; Owner: vboxuser
--

CREATE TRIGGER trigger_notify_projects_delete AFTER DELETE ON public.projects FOR EACH ROW EXECUTE FUNCTION public.notify_changes_after_insert();


--
-- Name: projects trigger_notify_projects_insert; Type: TRIGGER; Schema: public; Owner: vboxuser
--

CREATE TRIGGER trigger_notify_projects_insert AFTER INSERT ON public.projects FOR EACH ROW EXECUTE FUNCTION public.notify_changes_after_insert();


--
-- Name: projects trigger_notify_projects_update; Type: TRIGGER; Schema: public; Owner: vboxuser
--

CREATE TRIGGER trigger_notify_projects_update AFTER UPDATE ON public.projects FOR EACH ROW EXECUTE FUNCTION public.notify_changes_after_insert();


--
-- Name: tasks trigger_notify_tasks_delete; Type: TRIGGER; Schema: public; Owner: vboxuser
--

CREATE TRIGGER trigger_notify_tasks_delete AFTER DELETE ON public.tasks FOR EACH ROW EXECUTE FUNCTION public.notify_changes_after_insert();


--
-- Name: tasks trigger_notify_tasks_insert; Type: TRIGGER; Schema: public; Owner: vboxuser
--

CREATE TRIGGER trigger_notify_tasks_insert AFTER INSERT ON public.tasks FOR EACH ROW EXECUTE FUNCTION public.notify_changes_after_insert();


--
-- Name: tasks trigger_notify_tasks_update; Type: TRIGGER; Schema: public; Owner: vboxuser
--

CREATE TRIGGER trigger_notify_tasks_update AFTER UPDATE ON public.tasks FOR EACH ROW EXECUTE FUNCTION public.notify_changes_after_insert();


--
-- Name: messages messages_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id);


--
-- Name: messages messages_session_participant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_session_participant_id_fkey FOREIGN KEY (session_participant_id) REFERENCES public.session_participants(participant_id);


--
-- Name: session_participants session_participants_session_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.session_participants
    ADD CONSTRAINT session_participants_session_uuid_fkey FOREIGN KEY (session_uuid) REFERENCES public.sessions(session_id);


--
-- Name: sessions sessions_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id);


--
-- Name: tasks_enrichment tasks_enrichment_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.tasks_enrichment
    ADD CONSTRAINT tasks_enrichment_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: tasks tasks_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vboxuser
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(project_id);


--
-- Name: DATABASE nonidb; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON DATABASE nonidb TO vboxuser;


--
-- PostgreSQL database dump complete
--

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'LATIN1';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database cluster dump complete
--

