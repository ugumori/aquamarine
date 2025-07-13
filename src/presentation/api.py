from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from application.services import DeviceService, GPIOService
from application.models import (
    DeviceRegisterRequest, DeviceRegisterResponse, DeviceListResponse,
    DeviceStatusResponse, GPIOStatusResponse, DeviceDeleteResponse,
    DeviceUpdateRequest, DeviceUpdateResponse
)
from infrastructure.database import get_db
from infrastructure.repositories import SQLAlchemyDeviceRepository
from hardware.gpio_controller import RaspberryPiGPIOController, MockGPIOController
import os

app = FastAPI(title="Aquamarine IoT API", version="1.0.0")

# GPIO Controller の選択
def get_gpio_controller():
    if os.getenv("ENVIRONMENT") == "test":
        return MockGPIOController()
    else:
        return RaspberryPiGPIOController()

gpio_controller = get_gpio_controller()

def get_device_service(db: Session = Depends(get_db)) -> DeviceService:
    device_repository = SQLAlchemyDeviceRepository(db)
    return DeviceService(device_repository, gpio_controller)

def get_gpio_service() -> GPIOService:
    return GPIOService(gpio_controller)

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

@app.get("/health")
def health_check():
    return {"status": "healthy"}