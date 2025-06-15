import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# データベースの種類を環境変数から取得（デフォルトはsqlite）
DB_TYPE = os.getenv("DB_TYPE", "sqlite")

if DB_TYPE == "postgresql":
    # PostgreSQLの設定
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "15432")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "aquamarine")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # SQLiteの設定
    DB_PATH = os.getenv("DB_PATH", "aquamarine.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLiteの場合はcheck_same_thread=Falseを設定
connect_args = {"check_same_thread": False} if DB_TYPE == "sqlite" else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    # SQLiteの場合はecho=TrueでSQLログを出力（開発時のみ）
    echo=DB_TYPE == "sqlite" and os.getenv("DEBUG", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
