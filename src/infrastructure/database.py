import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.models import Base

# テスト環境の場合は、in-memoryデータベースを使用
if os.getenv("ENVIRONMENT") == "test":
    DATABASE_URL = "sqlite:///:memory:"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aquamarine.db")

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()