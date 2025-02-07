from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql://postgres:Mohsen#1367@localhost:5432/resa_fastapi"

# create a postgres engine instance
engine = create_engine(DATABASE_URL)


# Create declarative base meta instance
class Base(DeclarativeBase):
    pass


# Create session local class for session marker
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
