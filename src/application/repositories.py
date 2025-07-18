from abc import ABC, abstractmethod
from typing import List, Optional
from infrastructure.models import Device, Schedule

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
    
    @abstractmethod
    def delete(self, device_id: str) -> bool:
        pass
    
    @abstractmethod
    def update_device(self, device_id: str, device_name: Optional[str] = None, gpio_number: Optional[int] = None) -> bool:
        pass

class ScheduleRepository(ABC):
    @abstractmethod
    def save(self, schedule: Schedule) -> Schedule:
        pass
    
    @abstractmethod
    def find_by_device_id(self, device_id: str) -> List[Schedule]:
        pass
    
    @abstractmethod
    def find_by_id(self, schedule_id: str) -> Optional[Schedule]:
        pass
    
    @abstractmethod
    def delete(self, schedule_id: str) -> bool:
        pass