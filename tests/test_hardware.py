import pytest
from hardware.gpio_controller import MockGPIOController, RaspberryPiGPIOController

@pytest.fixture
def mock_gpio_controller():
    """MockGPIOControllerのフィクスチャ"""
    return MockGPIOController()

def test_mock_gpio_setup_pin(mock_gpio_controller):
    """GPIO ピンセットアップのテスト"""
    pin_number = 18
    mock_gpio_controller.setup_pin(pin_number)
    
    # 初期状態はFalse
    assert mock_gpio_controller.get_status(pin_number) == False
    assert pin_number in mock_gpio_controller._pin_states

def test_mock_gpio_turn_on(mock_gpio_controller):
    """GPIO ON操作のテスト"""
    pin_number = 18
    
    # ピンを ON にする
    mock_gpio_controller.turn_on(pin_number)
    
    # 状態がTrueになっているか確認
    assert mock_gpio_controller.get_status(pin_number) == True

def test_mock_gpio_turn_off(mock_gpio_controller):
    """GPIO OFF操作のテスト"""
    pin_number = 18
    
    # 最初にONにしてからOFFにする
    mock_gpio_controller.turn_on(pin_number)
    assert mock_gpio_controller.get_status(pin_number) == True
    
    mock_gpio_controller.turn_off(pin_number)
    assert mock_gpio_controller.get_status(pin_number) == False

def test_mock_gpio_get_status(mock_gpio_controller):
    """GPIO状態取得のテスト"""
    pin_number = 18
    
    # 初期状態
    status = mock_gpio_controller.get_status(pin_number)
    assert status == False
    
    # ONにしてから状態確認
    mock_gpio_controller.turn_on(pin_number)
    status = mock_gpio_controller.get_status(pin_number)
    assert status == True
    
    # OFFにしてから状態確認
    mock_gpio_controller.turn_off(pin_number)
    status = mock_gpio_controller.get_status(pin_number)
    assert status == False

def test_mock_gpio_multiple_pins(mock_gpio_controller):
    """複数のGPIOピンの操作テスト"""
    pin1, pin2 = 18, 19
    
    # 異なるピンを操作
    mock_gpio_controller.turn_on(pin1)
    mock_gpio_controller.turn_off(pin2)
    
    # それぞれの状態を確認
    assert mock_gpio_controller.get_status(pin1) == True
    assert mock_gpio_controller.get_status(pin2) == False
    
    # 逆の操作
    mock_gpio_controller.turn_off(pin1)
    mock_gpio_controller.turn_on(pin2)
    
    assert mock_gpio_controller.get_status(pin1) == False
    assert mock_gpio_controller.get_status(pin2) == True

def test_mock_gpio_auto_setup():
    """自動セットアップのテスト"""
    controller = MockGPIOController()
    pin_number = 20
    
    # setup_pin を呼ばずに直接操作
    controller.turn_on(pin_number)
    
    # 自動的にセットアップされて動作する
    assert controller.get_status(pin_number) == True
    assert pin_number in controller._pin_states

def test_raspberry_pi_gpio_controller_init():
    """RaspberryPiGPIOControllerの初期化テスト"""
    # Raspberry Pi環境でない場合のテスト
    controller = RaspberryPiGPIOController()
    
    # 初期化が正常に完了することを確認
    assert hasattr(controller, '_pin_states')
    assert isinstance(controller._pin_states, dict)

def test_raspberry_pi_gpio_controller_mock_behavior():
    """RaspberryPiGPIOControllerのモック動作テスト"""
    controller = RaspberryPiGPIOController()
    pin_number = 18
    
    # Raspberry Pi環境でない場合はMockと同様の動作
    controller.turn_on(pin_number)
    assert controller.get_status(pin_number) == True
    
    controller.turn_off(pin_number)
    assert controller.get_status(pin_number) == False