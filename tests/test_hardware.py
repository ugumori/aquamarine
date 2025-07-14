import pytest
from hardware.gpio_controller import RaspberryPiGPIOController
from hardware.gpio_factory import create_gpio_controller

@pytest.fixture
def gpio_controller():
    """環境に応じたGPIOControllerのフィクスチャ（開発環境ではMock、RaspberryPiでは実GPIO）"""
    return create_gpio_controller()

# 環境に応じたGPIOControllerテスト（Mockまたは実GPIO）
def test_gpio_setup_pin(gpio_controller):
    """GPIO ピンセットアップのテスト"""
    pin_number = 4
    gpio_controller.setup_pin(pin_number)
    
    # 初期状態はFalse
    assert gpio_controller.get_status(pin_number) == False

def test_gpio_turn_on(gpio_controller):
    """GPIO ON操作のテスト"""
    pin_number = 4
    
    # ピンを ON にする
    gpio_controller.turn_on(pin_number)
    
    # 状態がTrueになっているか確認
    assert gpio_controller.get_status(pin_number) == True

def test_gpio_turn_off(gpio_controller):
    """GPIO OFF操作のテスト"""
    pin_number = 4
    
    # 最初にONにしてからOFFにする
    gpio_controller.turn_on(pin_number)
    assert gpio_controller.get_status(pin_number) == True
    
    gpio_controller.turn_off(pin_number)
    assert gpio_controller.get_status(pin_number) == False

def test_gpio_get_status(gpio_controller):
    """GPIO状態取得のテスト"""
    pin_number = 4
    
    # 初期状態
    status = gpio_controller.get_status(pin_number)
    assert status == False
    
    # ONにしてから状態確認
    gpio_controller.turn_on(pin_number)
    status = gpio_controller.get_status(pin_number)
    assert status == True
    
    # OFFにしてから状態確認
    gpio_controller.turn_off(pin_number)
    status = gpio_controller.get_status(pin_number)
    assert status == False

def test_gpio_multiple_pins(gpio_controller):
    """複数のGPIOピンの操作テスト"""
    pin1, pin2 = 4, 19
    
    # 異なるピンを操作
    gpio_controller.turn_on(pin1)
    gpio_controller.turn_off(pin2)
    
    # それぞれの状態を確認
    assert gpio_controller.get_status(pin1) == True
    assert gpio_controller.get_status(pin2) == False
    
    # 逆の操作
    gpio_controller.turn_off(pin1)
    gpio_controller.turn_on(pin2)
    
    assert gpio_controller.get_status(pin1) == False
    assert gpio_controller.get_status(pin2) == True

def test_gpio_auto_setup(gpio_controller):
    """自動セットアップのテスト"""
    pin_number = 20
    
    # setup_pin を呼ばずに直接操作
    gpio_controller.turn_on(pin_number)
    
    # 自動的にセットアップされて動作する
    assert gpio_controller.get_status(pin_number) == True
