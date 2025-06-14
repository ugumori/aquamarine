from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

class DeviceRepository(ABC):
    @abstractmethod
    def create(self, device_id: str, device_name: str, gpio_number: int) -> None:
        pass

    @abstractmethod
    def find_all(self) -> List[tuple[str, str, int, datetime, datetime]]:
        pass

    @abstractmethod
    def find_by_id(self, device_id: str) -> Optional[tuple[str, str, int, datetime, datetime]]:
        pass

    @abstractmethod
    def update_timestamp(self, device_id: str) -> None:
        pass 
