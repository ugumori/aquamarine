"""Main module."""
import uvicorn
from src.infrastructure.models import Base
from src.infrastructure.database import engine

# データベースのテーブルを作成
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("src.presentation.api:app", host="localhost", port=80, reload=True) 
