from core.sql_interface import SQLInterface
from dotenv import load_dotenv
import os

load_dotenv("./environment/.env.development")

POSTGRE_CREDENTIALS = {
    "user": os.getenv('POSTGRE_USERNAME'),
    "password": os.getenv('POSTGRE_PASSWORD'),
    "host": os.getenv('POSTGRE_HOST'),
    "port": os.getenv('POSTGRE_PORT'),
    "database": os.getenv('POSTGRE_DATABASE')
}

def get_db():
    return SQLInterface.init_db_conn(POSTGRE_CREDENTIALS)