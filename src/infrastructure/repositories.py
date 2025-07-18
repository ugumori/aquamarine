from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
from application.repositories import DeviceRepository, ScheduleRepository
from infrastructure.models import Device, Schedule

class SQLAlchemyDeviceRepository(DeviceRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, device_id: str, device_name: str, gpio_number: int) -> None:
        device = Device(
            device_id=device_id,
            device_name=device_name,
            gpio_number=gpio_number
        )
        self.session.add(device)
        self.session.commit()
        self.session.refresh(device)

    def find_all(self) -> List[Device]:
        return self.session.query(Device).all()

    def find_by_id(self, device_id: str) -> Optional[Device]:
        return self.session.query(Device).filter(Device.device_id == device_id).first()

    def update_timestamp(self, device_id: str) -> None:
        device = self.session.query(Device).filter(Device.device_id == device_id).first()
        if device:
            device.updated_at = datetime.now()
            self.session.commit()

    def delete(self, device_id: str) -> bool:
        device = self.session.query(Device).filter(Device.device_id == device_id).first()
        if device:
            self.session.delete(device)
            self.session.commit()
            return True
        return False

    def update_device(self, device_id: str, device_name: Optional[str] = None, gpio_number: Optional[int] = None) -> bool:
        device = self.session.query(Device).filter(Device.device_id == device_id).first()
        if device:
            if device_name is not None:
                device.device_name = device_name
            if gpio_number is not None:
                device.gpio_number = gpio_number
            device.updated_at = datetime.now()
            self.session.commit()
            return True
        return False

class SQLAlchemyScheduleRepository(ScheduleRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, schedule: Schedule) -> Schedule:
        self.session.add(schedule)
        self.session.commit()
        self.session.refresh(schedule)
        return schedule
    
    def find_by_device_id(self, device_id: str) -> List[Schedule]:
        return self.session.query(Schedule).filter(
            Schedule.device_id == device_id
        ).order_by(Schedule.schedule).all()
    
    def find_by_id(self, schedule_id: str) -> Optional[Schedule]:
        return self.session.query(Schedule).filter(
            Schedule.schedule_id == schedule_id
        ).first()
    
    def delete(self, schedule_id: str) -> bool:
        schedule = self.session.query(Schedule).filter(
            Schedule.schedule_id == schedule_id
        ).first()
        if schedule:
            self.session.delete(schedule)
            self.session.commit()
            return True
        return False