import os
from abc import ABC, abstractmethod
from .gpio_platform import is_raspberry_pi
from log import logger

class GPIOController(ABC):
    @abstractmethod
    def setup_pin(self, pin_number: int) -> None:
        pass
    
    @abstractmethod
    def turn_on(self, pin_number: int) -> None:
        pass
    
    @abstractmethod
    def turn_off(self, pin_number: int) -> None:
        pass
    
    @abstractmethod
    def get_status(self, pin_number: int) -> bool:
        pass

class RaspberryPiGPIOController(GPIOController):
    def __init__(self):
        self._pin_states = {}
        # 実際のRaspberry Pi環境でのみGPIOライブラリを使用
        self._is_raspberry_pi = is_raspberry_pi()
        if self._is_raspberry_pi:
            logger.info(f"_is_raspberry_pi: {self._is_raspberry_pi}")
            try:
                import RPi.GPIO as GPIO
                self._GPIO = GPIO
                self._GPIO.setmode(GPIO.BCM)
                self._GPIO.setwarnings(False)
            except ImportError:
                logger.info(f"ImportError発生")
                self._is_raspberry_pi = False
    
    def setup_pin(self, pin_number: int) -> None:
        if self._is_raspberry_pi:
            self._GPIO.setup(pin_number, self._GPIO.OUT)
        self._pin_states[pin_number] = False
    
    def turn_on(self, pin_number: int) -> None:
        logger.info(f"_is_raspberry_pi: {self._is_raspberry_pi}")
        if pin_number not in self._pin_states:
            self.setup_pin(pin_number)
        
        if self._is_raspberry_pi:
            self._GPIO.output(pin_number, self._GPIO.HIGH)
        self._pin_states[pin_number] = True
    
    def turn_off(self, pin_number: int) -> None:
        logger.info(f"_is_raspberry_pi: {self._is_raspberry_pi}")
        if pin_number not in self._pin_states:
            self.setup_pin(pin_number)
        
        if self._is_raspberry_pi:
            self._GPIO.output(pin_number, self._GPIO.LOW)
        self._pin_states[pin_number] = False
    
    def get_status(self, pin_number: int) -> bool:
        if pin_number not in self._pin_states:
            self.setup_pin(pin_number)
        return self._pin_states[pin_number]

class MockGPIOController(GPIOController):
    def __init__(self):
        self._pin_states = {}
    
    def setup_pin(self, pin_number: int) -> None:
        self._pin_states[pin_number] = False
    
    def turn_on(self, pin_number: int) -> None:
        if pin_number not in self._pin_states:
            self.setup_pin(pin_number)
        self._pin_states[pin_number] = True
    
    def turn_off(self, pin_number: int) -> None:
        if pin_number not in self._pin_states:
            self.setup_pin(pin_number)
        self._pin_states[pin_number] = False
    
    def get_status(self, pin_number: int) -> bool:
        if pin_number not in self._pin_states:
            self.setup_pin(pin_number)
        return self._pin_states[pin_number]
