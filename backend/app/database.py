import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read the database URL from the environment variable set in docker-compose.yml
# e.g. "postgresql://tamu:devpassword@db:5432/grades"
# Note: inside Docker, "db" is the hostname — Docker's internal network resolves it
DATABASE_URL = os.environ["DATABASE_URL"]

# The engine is SQLAlchemy's connection to the database
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory for creating database sessions
# Each request gets its own session, which is closed when the request is done
SessionLocal = sessionmaker(bind=engine)

# Base is the parent class for all our SQLAlchemy models
Base = declarative_base()


def get_db():
    # FastAPI dependency that provides a DB session to route handlers
    # The try/finally ensures the session is always closed after the request,
    # even if an error occurs
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
