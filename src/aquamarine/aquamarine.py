"""Main module."""
import uvicorn

from infrastructure.models import Base
from infrastructure.database import engine

# データベースのテーブルを作成
Base.metadata.create_all(bind=engine)

def main():
    print("Start Aquamarine")
    uvicorn.run("presentation.api:app", host="localhost", port=8000, reload=True) 

if __name__ == "__main__":
    main()
