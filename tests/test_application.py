import pytest
from fastapi import HTTPException
from application.services import DeviceService, GPIOService, ScheduleService
from application.models import DeviceRegisterRequest, DeviceUpdateRequest, ScheduleCreateRequest
from infrastructure.models import Device, Schedule
from infrastructure.repositories import SQLAlchemyDeviceRepository, SQLAlchemyScheduleRepository
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

@pytest.fixture
def schedule_repository(test_db):
    """ScheduleRepositoryのフィクスチャ"""
    return SQLAlchemyScheduleRepository(test_db)

@pytest.fixture
def schedule_service(schedule_repository, device_repository):
    """ScheduleServiceのフィクスチャ"""
    return ScheduleService(schedule_repository, device_repository)

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

def test_delete_device_success(device_service, device_repository):
    """デバイス削除成功のテスト"""
    # デバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    
    # 実行
    response = device_service.delete_device("test-device")
    
    # 検証
    assert response.message == "Device deleted successfully"
    assert response.device_id == "test-device"
    
    # デバイスが削除されたことを確認
    deleted_device = device_repository.find_by_id("test-device")
    assert deleted_device is None

def test_delete_device_not_found(device_service):
    """デバイス削除（デバイスが存在しない）のテスト"""
    # 実行と検証
    with pytest.raises(HTTPException) as exc_info:
        device_service.delete_device("non-existent-device")
    
    assert exc_info.value.status_code == 404
    assert "Device not found" in str(exc_info.value.detail)

def test_update_device_name_only(device_service, device_repository):
    """デバイス名のみ更新のテスト"""
    # デバイスを作成
    device_repository.create("test-device", "Original Device", 18)
    
    # 実行
    request = DeviceUpdateRequest(device_name="Updated Device")
    response = device_service.update_device("test-device", request)
    
    # 検証
    assert response.device_name == "Updated Device"
    assert response.gpio_number == 18  # GPIO番号は変更されない
    assert response.device_id == "test-device"

def test_update_device_gpio_only(device_service, device_repository):
    """GPIO番号のみ更新のテスト"""
    # デバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    
    # 実行
    request = DeviceUpdateRequest(gpio_number=19)
    response = device_service.update_device("test-device", request)
    
    # 検証
    assert response.device_name == "Test Device"  # デバイス名は変更されない
    assert response.gpio_number == 19
    assert response.device_id == "test-device"

def test_update_device_both_name_and_gpio(device_service, device_repository):
    """デバイス名とGPIO番号両方更新のテスト"""
    # デバイスを作成
    device_repository.create("test-device", "Original Device", 18)
    
    # 実行
    request = DeviceUpdateRequest(device_name="Updated Device", gpio_number=20)
    response = device_service.update_device("test-device", request)
    
    # 検証
    assert response.device_name == "Updated Device"
    assert response.gpio_number == 20
    assert response.device_id == "test-device"

def test_update_device_no_parameters(device_service, device_repository):
    """更新パラメータなしのテスト"""
    # デバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    
    # 実行と検証
    request = DeviceUpdateRequest()
    with pytest.raises(HTTPException) as exc_info:
        device_service.update_device("test-device", request)
    
    assert exc_info.value.status_code == 400
    assert "No update parameters provided" in str(exc_info.value.detail)

def test_update_device_not_found(device_service):
    """存在しないデバイス更新のテスト"""
    # 実行と検証
    request = DeviceUpdateRequest(device_name="Updated Device")
    with pytest.raises(HTTPException) as exc_info:
        device_service.update_device("non-existent", request)
    
    assert exc_info.value.status_code == 404
    assert "Device not found" in str(exc_info.value.detail)

def test_update_device_gpio_conflict(device_service, device_repository):
    """GPIO競合エラーのテスト"""
    # 既存デバイスを作成
    device_repository.create("existing-device", "Existing Device", 19)
    # 更新対象デバイスを作成
    device_repository.create("target-device", "Target Device", 18)
    
    # 実行と検証（既存のGPIO 19に変更しようとする）
    request = DeviceUpdateRequest(gpio_number=19)
    with pytest.raises(HTTPException) as exc_info:
        device_service.update_device("target-device", request)
    
    assert exc_info.value.status_code == 400
    assert "GPIO 19 is already in use" in str(exc_info.value.detail)

def test_turn_device_on_not_found(device_service):
    """存在しないデバイスのON操作のテスト"""
    # 実行と検証
    with pytest.raises(HTTPException) as exc_info:
        device_service.turn_device_on("non-existent-device")
    
    assert exc_info.value.status_code == 404
    assert "Device not found" in str(exc_info.value.detail)

def test_turn_device_off_not_found(device_service):
    """存在しないデバイスのOFF操作のテスト"""
    # 実行と検証
    with pytest.raises(HTTPException) as exc_info:
        device_service.turn_device_off("non-existent-device")
    
    assert exc_info.value.status_code == 404
    assert "Device not found" in str(exc_info.value.detail)

# スケジュールサービスのテスト
def test_create_schedule_success(schedule_service, device_repository):
    """スケジュール作成成功のテスト"""
    # 依存するデバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    
    # テストデータ
    request = ScheduleCreateRequest(schedule="10:30", is_on=True)
    
    # 実行
    response = schedule_service.create_schedule("test-device", request)
    
    # 検証
    assert response.schedule == "10:30"
    assert response.is_on == True
    assert response.schedule_id is not None
    assert response.device_id == "test-device"
    assert response.created_at is not None

def test_create_schedule_device_not_found(schedule_service):
    """存在しないデバイスへのスケジュール作成のテスト"""
    # テストデータ
    request = ScheduleCreateRequest(schedule="10:30", is_on=True)
    
    # 実行と検証
    with pytest.raises(HTTPException) as exc_info:
        schedule_service.create_schedule("non-existent-device", request)
    
    assert exc_info.value.status_code == 400
    assert "Device not found" in str(exc_info.value.detail)

def test_create_schedule_invalid_time_format(schedule_service, device_repository):
    """不正な時間形式のスケジュール作成のテスト"""
    # 依存するデバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    
    # 不正な時間形式のテストケース
    invalid_times = ["25:00", "12:60", "abc:de", "12", "12:30:45", "-1:30"]
    
    for invalid_time in invalid_times:
        request = ScheduleCreateRequest(schedule=invalid_time, is_on=True)
        
        # 実行と検証
        with pytest.raises(HTTPException) as exc_info:
            schedule_service.create_schedule("test-device", request)
        
        assert exc_info.value.status_code == 400
        assert "Invalid time format" in str(exc_info.value.detail)

def test_create_schedule_valid_time_formats(schedule_service, device_repository):
    """有効な時間形式のスケジュール作成のテスト"""
    # 依存するデバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    
    # 有効な時間形式のテストケース
    valid_times = ["00:00", "12:30", "23:59", "9:05", "01:01"]
    
    for valid_time in valid_times:
        request = ScheduleCreateRequest(schedule=valid_time, is_on=True)
        
        # 実行
        response = schedule_service.create_schedule("test-device", request)
        
        # 検証
        assert response.schedule == valid_time
        assert response.is_on == True

def test_get_schedules_by_device_id_success(schedule_service, device_repository):
    """デバイスIDによるスケジュール取得成功のテスト"""
    # 依存するデバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    
    # スケジュールを作成
    request1 = ScheduleCreateRequest(schedule="18:00", is_on=False)
    request2 = ScheduleCreateRequest(schedule="10:00", is_on=True)
    
    schedule_service.create_schedule("test-device", request1)
    schedule_service.create_schedule("test-device", request2)
    
    # 実行
    response = schedule_service.get_schedules_by_device_id("test-device")
    
    # 検証（時間順でソートされている）
    assert len(response.schedules) == 2
    assert response.schedules[0].schedule == "10:00"
    assert response.schedules[0].is_on == True
    assert response.schedules[1].schedule == "18:00"
    assert response.schedules[1].is_on == False

def test_get_schedules_by_device_id_device_not_found(schedule_service):
    """存在しないデバイスのスケジュール取得のテスト"""
    # 実行と検証
    with pytest.raises(HTTPException) as exc_info:
        schedule_service.get_schedules_by_device_id("non-existent-device")
    
    assert exc_info.value.status_code == 404
    assert "Device not found" in str(exc_info.value.detail)

def test_get_schedules_by_device_id_empty_list(schedule_service, device_repository):
    """スケジュールがないデバイスの取得のテスト"""
    # 依存するデバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    
    # 実行
    response = schedule_service.get_schedules_by_device_id("test-device")
    
    # 検証
    assert len(response.schedules) == 0

def test_delete_schedule_success(schedule_service, device_repository):
    """スケジュール削除成功のテスト"""
    # 依存するデバイスを作成
    device_repository.create("test-device", "Test Device", 18)
    
    # スケジュールを作成
    request = ScheduleCreateRequest(schedule="10:30", is_on=True)
    created_schedule = schedule_service.create_schedule("test-device", request)
    
    # 実行
    schedule_service.delete_schedule(created_schedule.schedule_id)
    
    # 検証（スケジュールが削除されたことを確認）
    response = schedule_service.get_schedules_by_device_id("test-device")
    assert len(response.schedules) == 0

def test_delete_schedule_not_found(schedule_service):
    """存在しないスケジュール削除のテスト"""
    # 実行と検証
    with pytest.raises(HTTPException) as exc_info:
        schedule_service.delete_schedule("non-existent-schedule")
    
    assert exc_info.value.status_code == 404
    assert "Schedule not found" in str(exc_info.value.detail)
