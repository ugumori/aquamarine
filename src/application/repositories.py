from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from infrastructure.models import Device

class DeviceRepository(ABC):
    @abstractmethod
    def create(self, device_id: str, device_name: str, gpio_number: int) -> None:
        pass

    @abstractmethod
    def find_all(self) -> List[Device]:
        pass

    @abstractmethod
    def find_by_id(self, device_id: str) -> Optional[Device]:
        pass

    @abstractmethod
    def update_timestamp(self, device_id: str) -> None:
        pass 
