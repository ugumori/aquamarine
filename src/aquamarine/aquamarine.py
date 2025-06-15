"""Main module."""
import uvicorn
import logging

from infrastructure.models import Base
from infrastructure.database import engine

# ログの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# データベースのテーブルを作成
Base.metadata.create_all(bind=engine)

def main():
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
