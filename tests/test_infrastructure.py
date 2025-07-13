import pytest
from datetime import datetime
from infrastructure.models import Device
from infrastructure.repositories import SQLAlchemyDeviceRepository

@pytest.fixture
def device_repository(test_db):
    """デバイスリポジトリのフィクスチャ"""
    return SQLAlchemyDeviceRepository(test_db)

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