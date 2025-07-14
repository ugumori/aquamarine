import os
from abc import ABC, abstractmethod
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
        import RPi.GPIO as GPIO
        self._GPIO = GPIO
        self._GPIO.setmode(GPIO.BCM)
        self._GPIO.setwarnings(False)
    
    def setup_pin(self, pin_number: int) -> None:
        self._GPIO.setup(pin_number, self._GPIO.OUT)
        self._pin_states[pin_number] = False
    
    def turn_on(self, pin_number: int) -> None:
        if pin_number not in self._pin_states:
            self.setup_pin(pin_number)
        
        self._GPIO.output(pin_number, self._GPIO.HIGH)
        self._pin_states[pin_number] = True
    
    def turn_off(self, pin_number: int) -> None:
        if pin_number not in self._pin_states:
            self.setup_pin(pin_number)
        
        self._GPIO.output(pin_number, self._GPIO.LOW)
        self._pin_states[pin_number] = False
    
    def get_status(self, pin_number: int) -> bool:
        if pin_number not in self._pin_states:
            self.setup_pin(pin_number)
        
        return self._GPIO.input(pin_number)

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
