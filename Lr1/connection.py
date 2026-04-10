import os

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

load_dotenv()

database_url = os.getenv("DB_TIME")

if not database_url:
    raise ValueError("DB_TIME environment variable is not set")

engine = create_engine(database_url, echo=False)


def get_session():
    with Session(engine) as db_session:
        yield db_session
