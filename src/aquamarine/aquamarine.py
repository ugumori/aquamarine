"""Main module."""
import uvicorn
from infrastructure.models import Base
from infrastructure.database import engine
from log import logger

# データベースのテーブルを作成
Base.metadata.create_all(bind=engine)

def main():
    logger.info("Start Aquamarine")
    uvicorn.run(
        "presentation.api:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="debug",
        access_log=True
    )

if __name__ == "__main__":
    main()
