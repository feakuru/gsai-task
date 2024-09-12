from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# for this app, the database is just an SQLite file, in reality it would be something like Postgres
SQLALCHEMY_DATABASE_URL = "sqlite:///./gsai_records.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
