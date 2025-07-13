from infrastructure.models import Device
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
