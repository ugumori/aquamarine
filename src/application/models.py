from datetime import datetime
from pydantic import BaseModel
from typing import List

class DeviceRegisterRequest(BaseModel):
    device_name: str
    gpio_number: int

class DeviceRegisterResponse(BaseModel):
    device_id: str
    device_name: str
    gpio_number: int
    created_at: datetime
    updated_at: datetime

class DeviceDTO(BaseModel):
    device_id: str
    device_name: str
    gpio_number: int
    is_on: bool
    created_at: datetime
    updated_at: datetime

class DeviceListResponse(BaseModel):
    devices: List[DeviceDTO] 
