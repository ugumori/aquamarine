import pytest
import os
from fastapi.testclient import TestClient
from presentation.api import app
from infrastructure.database import create_tables, SessionLocal
from infrastructure.models import Device, Schedule

# テスト環境でMockGPIOControllerを使用
os.environ["ENVIRONMENT"] = "test"

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """テスト開始時にテーブルを作成"""
    create_tables()

@pytest.fixture
def test_db():
    """テスト用データベースセッション（テストデータ作成用）"""
    db = SessionLocal()
    # テスト前にクリーンアップ（外部キー制約を考慮してScheduleから削除）
    db.query(Schedule).delete()
    db.query(Device).delete()
    db.commit()
    yield db
    # テスト後にもクリーンアップ
    try:
        db.query(Schedule).delete()
        db.query(Device).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

@pytest.fixture
def client():
    """FastAPIテストクライアント"""
    with TestClient(app) as client:
        yield client