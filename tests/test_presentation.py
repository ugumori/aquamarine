from infrastructure.models import Device, Schedule
from datetime import datetime

def test_health_check(client):
    """ヘルスチェックのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_register_device_success(client, test_db):
    """デバイス登録成功のテスト"""
    # テストデータ
    device_data = {
        "device_name": "Test LED",
        "gpio_number": 18
    }
    
    # 実行
    response = client.post("/device/register", json=device_data)
    
    # 検証
    assert response.status_code == 200
    data = response.json()
    assert data["device_name"] == "Test LED"
    assert data["gpio_number"] == 18
    assert "device_id" in data

def test_register_device_gpio_conflict(client, test_db):
    """GPIO競合エラーのテスト"""
    # 既存デバイスを作成
    existing_device = Device(
        device_id="existing-device",
        device_name="Existing Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(existing_device)
    test_db.commit()
    
    # テストデータ
    device_data = {
        "device_name": "New Device",
        "gpio_number": 18
    }
    
    # 実行
    response = client.post("/device/register", json=device_data)
    
    # 検証
    assert response.status_code == 400
    assert "GPIO 18 is already in use" in response.json()["detail"]

def test_get_device_list(client, test_db):
    """デバイス一覧取得のテスト"""
    # テストデータを作成
    device1 = Device(
        device_id="device-1",
        device_name="Device 1",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    device2 = Device(
        device_id="device-2",
        device_name="Device 2",
        gpio_number=19,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device1)
    test_db.add(device2)
    test_db.commit()
    
    # 実行
    response = client.get("/device/list")
    
    # 検証
    assert response.status_code == 200
    data = response.json()
    assert len(data["devices"]) == 2
    assert data["devices"][0]["device_name"] == "Device 1"
    assert data["devices"][1]["device_name"] == "Device 2"

def test_get_device_status_success(client, test_db):
    """デバイス状態取得成功のテスト"""
    # テストデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Test Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # 実行
    response = client.get("/device/test-device/status")
    
    # 検証
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == "test-device"
    assert data["device_name"] == "Test Device"
    assert data["gpio_number"] == 18
    assert "is_on" in data

def test_get_device_status_not_found(client):
    """デバイス状態取得（デバイスが存在しない）のテスト"""
    # 実行
    response = client.get("/device/non-existent/status")
    
    # 検証
    assert response.status_code == 404
    assert "Device not found" in response.json()["detail"]

def test_turn_device_on(client, test_db):
    """デバイスON操作のテスト"""
    # テストデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Test Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # 実行
    response = client.post("/device/test-device/on")
    
    # 検証
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == "test-device"
    assert data["is_on"] == True

def test_turn_device_off(client, test_db):
    """デバイスOFF操作のテスト"""
    # テストデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Test Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # 実行
    response = client.post("/device/test-device/off")
    
    # 検証
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == "test-device"
    assert data["is_on"] == False

def test_gpio_operations(client):
    """GPIO直接操作のテスト"""
    # GPIO ON
    response = client.post("/GPIO/18/on")
    assert response.status_code == 200
    data = response.json()
    assert data["gpio_number"] == 18
    assert data["is_on"] == True
    
    # GPIO Status
    response = client.get("/GPIO/18/status")
    assert response.status_code == 200
    data = response.json()
    assert data["gpio_number"] == 18
    assert data["is_on"] == True
    
    # GPIO OFF
    response = client.post("/GPIO/18/off")
    assert response.status_code == 200
    data = response.json()
    assert data["gpio_number"] == 18
    assert data["is_on"] == False

def test_delete_device_success(client, test_db):
    """デバイス削除成功のテスト"""
    # テストデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Test Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # 実行
    response = client.delete("/device/test-device")
    
    # 検証
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Device deleted successfully"
    assert data["device_id"] == "test-device"

def test_delete_device_not_found(client):
    """デバイス削除（デバイスが存在しない）のテスト"""
    # 実行
    response = client.delete("/device/non-existent")
    
    # 検証
    assert response.status_code == 404
    assert "Device not found" in response.json()["detail"]

def test_update_device_name_only(client, test_db):
    """デバイス名のみ更新のテスト"""
    # テストデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Original Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # 実行
    update_data = {"device_name": "Updated Device"}
    response = client.put("/device/test-device", json=update_data)
    
    # 検証
    assert response.status_code == 200
    data = response.json()
    assert data["device_name"] == "Updated Device"
    assert data["gpio_number"] == 18  # GPIO番号は変更されない
    assert data["device_id"] == "test-device"

def test_update_gpio_only(client, test_db):
    """GPIO番号のみ更新のテスト"""
    # テストデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Test Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # 実行
    update_data = {"gpio_number": 19}
    response = client.put("/device/test-device", json=update_data)
    
    # 検証
    assert response.status_code == 200
    data = response.json()
    assert data["device_name"] == "Test Device"  # デバイス名は変更されない
    assert data["gpio_number"] == 19
    assert data["device_id"] == "test-device"

def test_update_both_name_and_gpio(client, test_db):
    """デバイス名とGPIO番号両方更新のテスト"""
    # テストデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Original Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # 実行
    update_data = {"device_name": "Updated Device", "gpio_number": 20}
    response = client.put("/device/test-device", json=update_data)
    
    # 検証
    assert response.status_code == 200
    data = response.json()
    assert data["device_name"] == "Updated Device"
    assert data["gpio_number"] == 20
    assert data["device_id"] == "test-device"

def test_update_device_no_parameters(client, test_db):
    """更新パラメータなしのテスト"""
    # テストデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Test Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # 実行
    update_data = {}
    response = client.put("/device/test-device", json=update_data)
    
    # 検証
    assert response.status_code == 400
    assert "No update parameters provided" in response.json()["detail"]

def test_update_device_not_found(client):
    """存在しないデバイス更新のテスト"""
    # 実行
    update_data = {"device_name": "Updated Device"}
    response = client.put("/device/non-existent", json=update_data)
    
    # 検証
    assert response.status_code == 404
    assert "Device not found" in response.json()["detail"]

def test_update_device_gpio_conflict(client, test_db):
    """GPIO競合エラーのテスト"""
    # 既存デバイス1を作成
    existing_device = Device(
        device_id="existing-device",
        device_name="Existing Device",
        gpio_number=19,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(existing_device)
    
    # 更新対象デバイスを作成
    target_device = Device(
        device_id="target-device",
        device_name="Target Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(target_device)
    test_db.commit()
    
    # 実行（既存のGPIO 19に変更しようとする）
    update_data = {"gpio_number": 19}
    response = client.put("/device/target-device", json=update_data)
    
    # 検証
    assert response.status_code == 400
    assert "GPIO 19 is already in use" in response.json()["detail"]

# スケジュールAPIのテスト
def test_create_schedule_success(client, test_db):
    """スケジュール作成成功のテスト"""
    # 依存するデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Test Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # テストデータ
    schedule_data = {
        "schedule": "10:30",
        "is_on": True
    }
    
    # 実行
    response = client.post("/schedule/test-device", json=schedule_data)
    
    # 検証
    assert response.status_code == 200
    data = response.json()
    assert data["schedule"] == "10:30"
    assert data["is_on"] == True
    assert data["device_id"] == "test-device"
    assert "schedule_id" in data
    assert "created_at" in data

def test_create_schedule_device_not_found(client):
    """存在しないデバイスへのスケジュール作成のテスト"""
    # テストデータ
    schedule_data = {
        "schedule": "10:30",
        "is_on": True
    }
    
    # 実行
    response = client.post("/schedule/non-existent", json=schedule_data)
    
    # 検証
    assert response.status_code == 400
    assert "Device not found" in response.json()["detail"]

def test_create_schedule_invalid_time_format(client, test_db):
    """不正な時間形式のスケジュール作成のテスト"""
    # 依存するデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Test Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # 不正な時間形式のテストケース
    invalid_times = ["25:00", "12:60", "abc:de", "12", "12:30:45"]
    
    for invalid_time in invalid_times:
        schedule_data = {
            "schedule": invalid_time,
            "is_on": True
        }
        
        # 実行
        response = client.post("/schedule/test-device", json=schedule_data)
        
        # 検証
        assert response.status_code == 400
        assert "Invalid time format" in response.json()["detail"]

def test_get_schedules_success(client, test_db):
    """スケジュール取得成功のテスト"""
    # 依存するデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Test Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # スケジュールを作成
    schedule1 = Schedule(
        schedule_id="schedule-1",
        device_id="test-device",
        schedule="18:00",
        is_on=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    schedule2 = Schedule(
        schedule_id="schedule-2",
        device_id="test-device",
        schedule="10:00",
        is_on=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(schedule1)
    test_db.add(schedule2)
    test_db.commit()
    
    # 実行
    response = client.get("/schedule/test-device")
    
    # 検証（時間順でソートされている）
    assert response.status_code == 200
    data = response.json()
    assert len(data["schedules"]) == 2
    assert data["schedules"][0]["schedule"] == "10:00"
    assert data["schedules"][0]["is_on"] == True
    assert data["schedules"][1]["schedule"] == "18:00"
    assert data["schedules"][1]["is_on"] == False

def test_get_schedules_device_not_found(client):
    """存在しないデバイスのスケジュール取得のテスト"""
    # 実行
    response = client.get("/schedule/non-existent")
    
    # 検証
    assert response.status_code == 404
    assert "Device not found" in response.json()["detail"]

def test_get_schedules_empty_list(client, test_db):
    """スケジュールがないデバイスの取得のテスト"""
    # 依存するデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Test Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # 実行
    response = client.get("/schedule/test-device")
    
    # 検証
    assert response.status_code == 200
    data = response.json()
    assert len(data["schedules"]) == 0

def test_delete_schedule_success(client, test_db):
    """スケジュール削除成功のテスト"""
    # 依存するデバイスを作成
    device = Device(
        device_id="test-device",
        device_name="Test Device",
        gpio_number=18,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(device)
    test_db.commit()
    
    # スケジュールを作成
    schedule = Schedule(
        schedule_id="test-schedule",
        device_id="test-device",
        schedule="10:30",
        is_on=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    test_db.add(schedule)
    test_db.commit()
    
    # 実行
    response = client.delete("/schedule/test-schedule")
    
    # 検証
    assert response.status_code == 204

def test_delete_schedule_not_found(client):
    """存在しないスケジュール削除のテスト"""
    # 実行
    response = client.delete("/schedule/non-existent")
    
    # 検証
    assert response.status_code == 404
    assert "Schedule not found" in response.json()["detail"]
