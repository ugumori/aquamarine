#!/usr/bin/env python3
"""Console script for aquamarine."""

import uvicorn
from infrastructure.database import create_tables, get_db
from infrastructure.repositories import SQLAlchemyDeviceRepository, SQLAlchemyScheduleRepository
from application.services import ScheduleExecutorService
from hardware.gpio_factory import create_gpio_controller

# グローバル変数として定義
schedule_executor = None

def main():
    """アプリケーションのエントリーポイント"""
    global schedule_executor
    
    # データベーステーブルを作成
    create_tables()
    
    # ScheduleExecutorServiceの初期化
    gpio_controller = create_gpio_controller()
    db = next(get_db())
    device_repository = SQLAlchemyDeviceRepository(db)
    
    schedule_executor = ScheduleExecutorService(device_repository, gpio_controller)
    schedule_executor.start()
    
    # 既存スケジュールを読み込んでスケジューラーに追加
    schedule_repository = SQLAlchemyScheduleRepository(db)
    existing_schedules = schedule_repository.find_all()
    
    for schedule in existing_schedules:
        try:
            schedule_executor.add_schedule(
                schedule.schedule_id,
                schedule.device_id,
                schedule.schedule,
                schedule.is_on
            )
        except Exception as e:
            print(f"Warning: Failed to load schedule {schedule.schedule_id}: {str(e)}")
    
    # FastAPIアプリケーションを起動
    uvicorn.run(
        "presentation.api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="debug",
        access_log=True,
    )

if __name__ == "__main__":
    main()