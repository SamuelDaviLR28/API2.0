from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

DATABASE_URL = "postgresql://api2_c7jj_user:1p3QXrmGAHQFwAukULQzqK2sRrLLlsKJ@dpg-d1e4jkmmcj7s73b286l0-a/api2_c7jj"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
