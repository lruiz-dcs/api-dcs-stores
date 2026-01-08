
import pyodbc
from app.core.config import Config

server   = Config.SERVER_HOST
database = Config.SERVER_DATABASE
username = Config.SERVER_DATABASE_USERNAME
password = Config.SERVER_DATABASE_PASSWORD


def get_connection():
    return pyodbc.connect(
        'DRIVER={SQL Server};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        'Trusted_Connection=no;'
    )

