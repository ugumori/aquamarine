from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

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

class DeviceUpdateRequest(BaseModel):
    device_name: Optional[str] = None
    gpio_number: Optional[int] = None

class DeviceUpdateResponse(BaseModel):
    device_id: str
    device_name: str
    gpio_number: int
    created_at: datetime
    updated_at: datetime

class ScheduleCreateRequest(BaseModel):
    schedule: str
    is_on: bool

class ScheduleModel(BaseModel):
    schedule_id: str
    schedule: str
    is_on: bool

class ScheduleCreateResponse(BaseModel):
    schedule_id: str
    device_id: str
    schedule: str
    is_on: bool
    created_at: datetime

class ScheduleListResponse(BaseModel):
    schedules: List[ScheduleModel]