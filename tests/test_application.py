import pytest
from fastapi import HTTPException
from application.services import DeviceService, GPIOService
from application.models import DeviceRegisterRequest
from infrastructure.models import Device
from infrastructure.repositories import SQLAlchemyDeviceRepository
from hardware.gpio_controller import MockGPIOController
from datetime import datetime

@pytest.fixture
def device_repository(test_db):
    """DeviceRepositoryのフィクスチャ"""
    return SQLAlchemyDeviceRepository(test_db)

@pytest.fixture
def gpio_controller():
    """GPIO Controllerのフィクスチャ"""
    return MockGPIOController()

@pytest.fixture
def device_service(device_repository, gpio_controller):
    """DeviceServiceのフィクスチャ"""
    return DeviceService(device_repository, gpio_controller)

@pytest.fixture
def gpio_service(gpio_controller):
    """GPIOServiceのフィクスチャ"""
    return GPIOService(gpio_controller)

def test_register_device_success(device_service):
    """デバイス登録成功のテスト"""
    # テストデータ
    request = DeviceRegisterRequest(device_name="Test LED", gpio_number=18)
    
    # 実行
    response = device_service.register_device(request)
    
    # 検証
    assert response.device_name == "Test LED"
    assert response.gpio_number == 18
    assert response.device_id is not None

def test_register_device_gpio_already_in_use(device_service, device_repository):
    """GPIO番号が既に使用中の場合のテスト"""
    # 既存デバイスを作成
    device_repository.create("existing-device", "Existing Device", 18)
    
    # テストデータ
    request = DeviceRegisterRequest(device_name="New Device", gpio_number=18)
    
    # 実行と検証
    with pytest.raises(HTTPException) as exc_info:
        device_service.register_device(request)
    
    assert exc_info.value.status_code == 400
    assert "GPIO 18 is already in use" in str(exc_info.value.detail)

def test_get_device_list(device_service, device_repository, gpio_controller):
    """デバイス一覧取得のテスト"""
    # デバイスを作成
    device_repository.create("device-1", "Device 1", 18)
    device_repository.create("device-2", "Device 2", 19)
    
    # GPIO状態の設定
    gpio_controller.turn_on(18)
    gpio_controller.turn_off(19)
    
    # 実行
    response = device_service.get_device_list()
    
    # 検証
    assert len(response.devices) == 2
    assert response.devices[0].device_name == "Device 1"
    assert response.devices[0].is_on == True
    assert response.devices[1].device_name == "Device 2"
    assert response.devices[1].is_on == False

def test_get_device_status_success(device_service, device_repository, gpio_controller):
    """デバイス状態取得成功のテスト"""
    # デバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    gpio_controller.turn_on(18)
    
    # 実行
    response = device_service.get_device_status("test-device")
    
    # 検証
    assert response.device_id == "test-device"
    assert response.device_name == "Test Device"
    assert response.gpio_number == 18
    assert response.is_on == True

def test_get_device_status_not_found(device_service):
    """デバイス状態取得（デバイスが存在しない）のテスト"""
    # 実行と検証
    with pytest.raises(HTTPException) as exc_info:
        device_service.get_device_status("non-existent-device")
    
    assert exc_info.value.status_code == 404
    assert "Device not found" in str(exc_info.value.detail)

def test_turn_device_on(device_service, device_repository, gpio_controller):
    """デバイスON操作のテスト"""
    # デバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    
    # 実行
    response = device_service.turn_device_on("test-device")
    
    # 検証
    assert response.device_id == "test-device"
    assert response.is_on == True
    assert gpio_controller.get_status(18) == True

def test_turn_device_off(device_service, device_repository, gpio_controller):
    """デバイスOFF操作のテスト"""
    # デバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    
    # 実行
    response = device_service.turn_device_off("test-device")
    
    # 検証
    assert response.device_id == "test-device"
    assert response.is_on == False
    assert gpio_controller.get_status(18) == False

def test_gpio_service_turn_on(gpio_service, gpio_controller):
    """GPIO ON操作のテスト"""
    # 実行
    response = gpio_service.turn_gpio_on(18)
    
    # 検証
    assert response.gpio_number == 18
    assert response.is_on == True
    assert gpio_controller.get_status(18) == True

def test_gpio_service_turn_off(gpio_service, gpio_controller):
    """GPIO OFF操作のテスト"""
    # 実行
    response = gpio_service.turn_gpio_off(18)
    
    # 検証
    assert response.gpio_number == 18
    assert response.is_on == False
    assert gpio_controller.get_status(18) == False

def test_gpio_service_get_status(gpio_service, gpio_controller):
    """GPIO状態取得のテスト"""
    # GPIO をONにしてから状態確認
    gpio_controller.turn_on(18)
    response = gpio_service.get_gpio_status(18)
    
    # 検証
    assert response.gpio_number == 18
    assert response.is_on == True