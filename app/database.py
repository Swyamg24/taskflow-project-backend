from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

DATABASE_URL = os.getenv("DATABASE_URL")

# create_engine = the connection to PostgreSQL
# pool_pre_ping=True = checks connection is alive before using it
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal = a factory that creates DB sessions
# Each request gets its own session, then it's closed
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = parent class for all SQLAlchemy models
Base = declarative_base()


# Dependency — FastAPI calls this for every route that needs DB access
# yield = gives the session to the route, then closes it when done
def get_db():
    db = SessionLocal()
    try:
        yield db          # route handler runs here
    finally:
        db.close()     