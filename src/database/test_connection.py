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
    f"postgresql://{user}:{password}"
    f"@{host}:{port}/{database}"
)

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful!")
        print(result.fetchone())

except Exception as e:
    print("Database connection failed:")
    print(e)