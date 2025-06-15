import RPi.GPIO as GPIO
from typing import Dict, Set

class GPIOController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self._used_pins: Set[int] = set()
        self._pin_states: Dict[int, bool] = {}

    def setup_pin(self, pin_number: int) -> None:
        GPIO.setup(pin_number, GPIO.OUT)
        self._used_pins.add(pin_number)
        self._pin_states[pin_number] = False

    def turn_on(self, pin_number: int) -> None:
        if pin_number not in self._used_pins:
            raise ValueError(f"GPIO pin {pin_number} is not set up")
        GPIO.output(pin_number, GPIO.HIGH)
        self._pin_states[pin_number] = True

    def turn_off(self, pin_number: int) -> None:
        if pin_number not in self._used_pins:
            raise ValueError(f"GPIO pin {pin_number} is not set up")
        GPIO.output(pin_number, GPIO.LOW)
        self._pin_states[pin_number] = False

    def get_status(self, pin_number: int) -> bool:
        if pin_number not in self._used_pins:
            raise ValueError(f"GPIO pin {pin_number} is not set up")
        return self._pin_states[pin_number]

    def cleanup(self) -> None:
        GPIO.cleanup()
        self._used_pins.clear()
        self._pin_states.clear()

# シングルトンインスタンス
gpio_controller = GPIOController() 
