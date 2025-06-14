from datetime import datetime, UTC
from sqlalchemy.orm import Session
from typing import List, Optional

from src.application.repositories import DeviceRepository
from src.infrastructure.models import Device

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

    def find_all(self) -> List[tuple[str, str, int, datetime, datetime]]:
        devices = self.session.query(Device).all()
        return [
            (device.device_id, device.device_name, device.gpio_number, device.created_at, device.updated_at)
            for device in devices
        ]

    def find_by_id(self, device_id: str) -> Optional[tuple[str, str, int, datetime, datetime]]:
        device = self.session.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            return None
        return (device.device_id, device.device_name, device.gpio_number, device.created_at, device.updated_at)

    def update_timestamp(self, device_id: str) -> None:
        device = self.session.query(Device).filter(Device.device_id == device_id).first()
        if device:
            device.updated_at = datetime.now(UTC)
            self.session.commit() 
