import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("POSTGRES_DB")
host = "localhost"
port = os.getenv("POSTGRES_PORT")

DATABASE_URL = (
    f"postgresql://{user}:{password}@{host}:{port}/{database}"
)

engine = create_engine(DATABASE_URL)