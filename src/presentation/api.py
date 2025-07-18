from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from application.services import DeviceService, GPIOService, ScheduleService, ScheduleExecutorService
from application.models import (
    DeviceRegisterRequest, DeviceRegisterResponse, DeviceListResponse,
    DeviceStatusResponse, GPIOStatusResponse, DeviceDeleteResponse,
    DeviceUpdateRequest, DeviceUpdateResponse, ScheduleCreateRequest,
    ScheduleCreateResponse, ScheduleListResponse
)
from infrastructure.database import get_db
from infrastructure.repositories import SQLAlchemyDeviceRepository, SQLAlchemyScheduleRepository
from hardware.gpio_factory import create_gpio_controller
import os
from aquamarine import schedule_executor

app = FastAPI(title="Aquamarine IoT API", version="1.0.0")


gpio_controller = create_gpio_controller()

def get_device_service(db: Session = Depends(get_db)) -> DeviceService:
    device_repository = SQLAlchemyDeviceRepository(db)
    return DeviceService(device_repository, gpio_controller)

def get_gpio_service() -> GPIOService:
    return GPIOService(gpio_controller)

def get_schedule_executor_service() -> ScheduleExecutorService:
    """ScheduleExecutorServiceを取得"""
    return schedule_executor

def get_schedule_service(db: Session = Depends(get_db), schedule_executor: ScheduleExecutorService = Depends(get_schedule_executor_service)) -> ScheduleService:
    schedule_repository = SQLAlchemyScheduleRepository(db)
    device_repository = SQLAlchemyDeviceRepository(db)
    return ScheduleService(schedule_repository, device_repository, schedule_executor)

@app.post("/device/register", response_model=DeviceRegisterResponse)
def register_device(
    request: DeviceRegisterRequest,
    service: DeviceService = Depends(get_device_service)
):
    return service.register_device(request)

@app.get("/device/list", response_model=DeviceListResponse)
def get_device_list(service: DeviceService = Depends(get_device_service)):
    return service.get_device_list()

@app.get("/device/{device_id}/status", response_model=DeviceStatusResponse)
def get_device_status(
    device_id: str,
    service: DeviceService = Depends(get_device_service)
):
    return service.get_device_status(device_id)

@app.post("/device/{device_id}/on", response_model=DeviceStatusResponse)
def turn_device_on(
    device_id: str,
    service: DeviceService = Depends(get_device_service)
):
    return service.turn_device_on(device_id)

@app.post("/device/{device_id}/off", response_model=DeviceStatusResponse)
def turn_device_off(
    device_id: str,
    service: DeviceService = Depends(get_device_service)
):
    return service.turn_device_off(device_id)

@app.delete("/device/{device_id}", response_model=DeviceDeleteResponse)
def delete_device(
    device_id: str,
    service: DeviceService = Depends(get_device_service)
):
    return service.delete_device(device_id)

@app.put("/device/{device_id}", response_model=DeviceUpdateResponse)
def update_device(
    device_id: str,
    request: DeviceUpdateRequest,
    service: DeviceService = Depends(get_device_service)
):
    return service.update_device(device_id, request)

@app.post("/GPIO/{gpio_number}/on", response_model=GPIOStatusResponse)
def turn_gpio_on(
    gpio_number: int,
    service: GPIOService = Depends(get_gpio_service)
):
    return service.turn_gpio_on(gpio_number)

@app.post("/GPIO/{gpio_number}/off", response_model=GPIOStatusResponse)
def turn_gpio_off(
    gpio_number: int,
    service: GPIOService = Depends(get_gpio_service)
):
    return service.turn_gpio_off(gpio_number)

@app.get("/GPIO/{gpio_number}/status", response_model=GPIOStatusResponse)
def get_gpio_status(
    gpio_number: int,
    service: GPIOService = Depends(get_gpio_service)
):
    return service.get_gpio_status(gpio_number)

@app.post("/schedule/{device_id}", response_model=ScheduleCreateResponse)
def create_schedule(
    device_id: str,
    request: ScheduleCreateRequest,
    service: ScheduleService = Depends(get_schedule_service)
):
    return service.create_schedule(device_id, request)

@app.get("/schedule/{device_id}", response_model=ScheduleListResponse)
def get_schedules(
    device_id: str,
    service: ScheduleService = Depends(get_schedule_service)
):
    return service.get_schedules_by_device_id(device_id)

@app.delete("/schedule/{schedule_id}", status_code=204)
def delete_schedule(
    schedule_id: str,
    service: ScheduleService = Depends(get_schedule_service)
):
    service.delete_schedule(schedule_id)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
