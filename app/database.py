from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from decouple import config


DATABASE_URL = config("DATABASE")

# create a postgres engine instance
engine = create_engine(DATABASE_URL, echo=config("ECHO", default=False, cast=bool))


# Create declarative base meta instance
class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
