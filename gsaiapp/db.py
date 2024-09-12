from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# for this app, the database is just an SQLite file, in reality it would be something like Postgres
SQLALCHEMY_DATABASE_URL = "sqlite:///./gsai_records.db"

# the engine used is the sync one - for simplicity, readability
# and also because SQLite does not benefit a lot from parallelization of requests,
# but in a production environment with Postgres it would be beneficial to use
# the async engine and add some more boilerplate for it
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
