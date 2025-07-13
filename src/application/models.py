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

class DeviceModel(BaseModel):
    device_id: str
    device_name: str
    gpio_number: int
    is_on: bool
    created_at: datetime
    updated_at: datetime

class DeviceListResponse(BaseModel):
    devices: List[DeviceModel]

class DeviceStatusResponse(BaseModel):
    device_id: str
    device_name: str
    gpio_number: int
    is_on: bool

class GPIOStatusResponse(BaseModel):
    gpio_number: int
    is_on: bool

class DeviceDeleteResponse(BaseModel):
    message: str
    device_id: str