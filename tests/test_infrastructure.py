import pytest
from datetime import datetime
from infrastructure.models import Device, Schedule
from infrastructure.repositories import SQLAlchemyDeviceRepository, SQLAlchemyScheduleRepository

@pytest.fixture
def device_repository(test_db):
    """デバイスリポジトリのフィクスチャ"""
    return SQLAlchemyDeviceRepository(test_db)

@pytest.fixture
def schedule_repository(test_db):
    """スケジュールリポジトリのフィクスチャ"""
    return SQLAlchemyScheduleRepository(test_db)

def test_device_model():
    """Deviceモデルのテスト"""
    device = Device(
        device_id="test-device-id",
        device_name="Test Device",
        gpio_number=18
    )
    
    assert device.device_id == "test-device-id"
    assert device.device_name == "Test Device"
    assert device.gpio_number == 18

def test_create_device(device_repository):
    """デバイス作成のテスト"""
    device_id = "test-device-123"
    device_name = "Test LED"
    gpio_number = 18
    
    device_repository.create(device_id, device_name, gpio_number)
    
    created_device = device_repository.find_by_id(device_id)
    assert created_device is not None
    assert created_device.device_id == device_id
    assert created_device.device_name == device_name
    assert created_device.gpio_number == gpio_number

def test_find_all_devices(device_repository):
    """全デバイス取得のテスト"""
    # 複数のデバイスを作成
    device_repository.create("device-1", "Device 1", 18)
    device_repository.create("device-2", "Device 2", 19)
    
    devices = device_repository.find_all()
    assert len(devices) == 2
    
    device_ids = [device.device_id for device in devices]
    assert "device-1" in device_ids
    assert "device-2" in device_ids

def test_find_device_by_id(device_repository):
    """IDによるデバイス取得のテスト"""
    device_id = "test-device-find"
    device_repository.create(device_id, "Test Device", 20)
    
    found_device = device_repository.find_by_id(device_id)
    assert found_device is not None
    assert found_device.device_id == device_id
    
    # 存在しないデバイスの場合
    non_existent_device = device_repository.find_by_id("non-existent")
    assert non_existent_device is None

def test_update_timestamp(device_repository):
    """タイムスタンプ更新のテスト"""
    device_id = "test-device-timestamp"
    device_repository.create(device_id, "Test Device", 21)
    
    original_device = device_repository.find_by_id(device_id)
    original_timestamp = original_device.updated_at
    
    # 少し待ってからタイムスタンプを更新
    import time
    time.sleep(0.1)
    
    device_repository.update_timestamp(device_id)
    
    updated_device = device_repository.find_by_id(device_id)
    assert updated_device.updated_at > original_timestamp

def test_schedule_model():
    """Scheduleモデルのテスト"""
    schedule = Schedule(
        schedule_id="test-schedule-id",
        device_id="test-device-id",
        schedule="10:00",
        is_on=True
    )
    
    assert schedule.schedule_id == "test-schedule-id"
    assert schedule.device_id == "test-device-id"
    assert schedule.schedule == "10:00"
    assert schedule.is_on is True

def test_schedule_repository_save(schedule_repository, device_repository):
    """スケジュール保存のテスト"""
    # 依存するデバイスを作成
    device_id = "test-device-save"
    device_repository.create(device_id, "Test Device", 18)
    
    # スケジュールを作成
    schedule = Schedule(
        schedule_id="test-schedule-save",
        device_id=device_id,
        schedule="10:00",
        is_on=True
    )
    
    saved_schedule = schedule_repository.save(schedule)
    
    assert saved_schedule.schedule_id == "test-schedule-save"
    assert saved_schedule.device_id == device_id
    assert saved_schedule.schedule == "10:00"
    assert saved_schedule.is_on is True

def test_schedule_repository_find_by_device_id(schedule_repository, device_repository):
    """デバイスIDによるスケジュール取得のテスト"""
    # 依存するデバイスを作成
    device_id = "test-device-find"
    device_repository.create(device_id, "Test Device", 18)
    
    # 複数のスケジュールを作成
    schedule1 = Schedule(
        schedule_id="schedule-1",
        device_id=device_id,
        schedule="10:00",
        is_on=True
    )
    schedule2 = Schedule(
        schedule_id="schedule-2",
        device_id=device_id,
        schedule="18:00",
        is_on=False
    )
    
    schedule_repository.save(schedule1)
    schedule_repository.save(schedule2)
    
    # 時間順で取得されることを確認
    schedules = schedule_repository.find_by_device_id(device_id)
    assert len(schedules) == 2
    assert schedules[0].schedule == "10:00"
    assert schedules[1].schedule == "18:00"

def test_schedule_repository_find_by_id(schedule_repository, device_repository):
    """スケジュールIDによる取得のテスト"""
    # 依存するデバイスを作成
    device_id = "test-device-id"
    device_repository.create(device_id, "Test Device", 18)
    
    # スケジュールを作成
    schedule = Schedule(
        schedule_id="test-schedule-find",
        device_id=device_id,
        schedule="10:00",
        is_on=True
    )
    schedule_repository.save(schedule)
    
    # 存在するスケジュールの取得
    found_schedule = schedule_repository.find_by_id("test-schedule-find")
    assert found_schedule is not None
    assert found_schedule.schedule_id == "test-schedule-find"
    
    # 存在しないスケジュールの取得
    not_found_schedule = schedule_repository.find_by_id("non-existent")
    assert not_found_schedule is None

def test_schedule_repository_delete(schedule_repository, device_repository):
    """スケジュール削除のテスト"""
    # 依存するデバイスを作成
    device_id = "test-device-delete"
    device_repository.create(device_id, "Test Device", 18)
    
    # スケジュールを作成
    schedule = Schedule(
        schedule_id="test-schedule-delete",
        device_id=device_id,
        schedule="10:00",
        is_on=True
    )
    schedule_repository.save(schedule)
    
    # 削除テスト
    result = schedule_repository.delete("test-schedule-delete")
    assert result is True
    
    # 削除されたことを確認
    deleted_schedule = schedule_repository.find_by_id("test-schedule-delete")
    assert deleted_schedule is None
    
    # 存在しないスケジュールの削除
    result = schedule_repository.delete("non-existent")
    assert result is False