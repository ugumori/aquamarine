from .gpio_controller import GPIOController, MockGPIOController, RaspberryPiGPIOController
from .gpio_platform import is_raspberry_pi

def create_gpio_controller(force_mock: bool = False) -> GPIOController:
    """
    GPIOControllerのインスタンスを作成する
    
    Args:
        force_mock: Trueの場合、RaspberryPi環境でもMockControllerを使用する
    
    Returns:
        GPIOController: RaspberryPi環境なら実際のGPIOController、そうでなければMockController
    """
    if force_mock or not is_raspberry_pi():
        return MockGPIOController()
    else:
        return RaspberryPiGPIOController()