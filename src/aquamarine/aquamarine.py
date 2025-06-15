"""Main module."""
import logging
import uvicorn

from infrastructure.models import Base
from infrastructure.database import engine

# データベースのテーブルを作成
Base.metadata.create_all(bind=engine)

def main():
    logger = logging.getLogger(__name__)
    logger.info("Start Aquamarine")
    uvicorn.run(
        "presentation.api:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="debug"
    )

if __name__ == "__main__":
    main()
