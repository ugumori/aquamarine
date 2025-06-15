from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from infrastructure.repositories import SQLAlchemyDeviceRepository
from application.device_service import DeviceService
from application.models import DeviceRegisterRequest, DeviceRegisterResponse, DeviceListResponse
from hardware.gpio_controller import gpio_controller
from log import logger

app = FastAPI()


def get_device_service(db: Session = Depends(get_db)) -> DeviceService:
    repository = SQLAlchemyDeviceRepository(db)
    return DeviceService(repository)

@app.post("/device", response_model=DeviceRegisterResponse)
def register_device(request: DeviceRegisterRequest, service: DeviceService = Depends(get_device_service)):
    logger.info(f"Registering device: {request.device_name}")
    try:
        return service.register_device(request)
    except ValueError as e:
        logger.error(f"Failed to register device: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/device/{device_id}")
def get_device(device_id: str, service: DeviceService = Depends(get_device_service)):
    logger.info(f"Getting device: {device_id}")
    try:
        status = service.get_device_status(device_id)
        return {"is_on": status}
    except ValueError as e:
        logger.error(f"Failed to get device: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/devices", response_model=DeviceListResponse)
def get_device_list(service: DeviceService = Depends(get_device_service)):
    logger.info("Getting device list")
    try:
        devices = service.get_device_list()
        logger.debug(f"Found {len(devices)} devices")
        return DeviceListResponse(devices=devices)
    except ValueError as e:
        logger.error(f"Failed to get device list: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/device/{device_id}/on")
def turn_on_device(device_id: str, service: DeviceService = Depends(get_device_service)):
    logger.info(f"Turning on device: {device_id}")
    try:
        service.turn_on_device(device_id)
        return {"message": "Device turned on successfully"}
    except ValueError as e:
        logger.error(f"Failed to turn on device: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/device/{device_id}/off")
def turn_off_device(device_id: str, service: DeviceService = Depends(get_device_service)):
    logger.info(f"Turning off device: {device_id}")
    try:
        service.turn_off_device(device_id)
        return {"message": "Device turned off successfully"}
    except ValueError as e:
        logger.error(f"Failed to turn off device: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/GPIO/{gpio_number}/on")
def turn_on_gpio(gpio_number: int):
    logger.info(f"Turning on GPIO: {gpio_number}")
    try:
        gpio_controller.setup_pin(gpio_number)
        gpio_controller.turn_on(gpio_number)
        return {"message": "GPIO turned on successfully"}
    except ValueError as e:
        logger.error(f"Failed to turn on GPIO: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/GPIO/{gpio_number}/off")
def turn_off_gpio(gpio_number: int):
    logger.info(f"Turning off GPIO: {gpio_number}")
    try:
        gpio_controller.setup_pin(gpio_number)
        gpio_controller.turn_off(gpio_number)
        return {"message": "GPIO turned off successfully"}
    except ValueError as e:
        logger.error(f"Failed to turn off GPIO: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/GPIO/{gpio_number}/status")
def get_gpio_status(gpio_number: int):
    logger.info(f"Getting GPIO status: {gpio_number}")
    try:
        gpio_controller.setup_pin(gpio_number)
        status = gpio_controller.get_status(gpio_number)
        return {"is_on": status}
    except ValueError as e:
        logger.error(f"Failed to get GPIO status: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) 
