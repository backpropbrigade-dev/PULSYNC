import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Fallback to SQLite if PostgreSQL URL is not provided in environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pulsync.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
