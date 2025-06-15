from datetime import datetime, UTC
from typing import List, Optional
import logging
from application.repositories import DeviceRepository
from hardware.gpio_controller import gpio_controller
from application.models import DeviceDTO, DeviceRegisterRequest, DeviceRegisterResponse
import uuid

logger = logging.getLogger(__name__)

class DeviceService:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository

    def register_device(self, request: DeviceRegisterRequest) -> DeviceRegisterResponse:
        logger.info(f"Registering device: {request.device_name}")
        # GPIOピンが使用中かチェック
        try:
            gpio_controller.setup_pin(request.gpio_number)
        except ValueError as e:
            logger.error(f"Failed to register device: {str(e)}")
            raise ValueError(f"Failed to register device: {str(e)}")

        # デバイスを登録
        device_id = str(uuid.uuid4())
        self.repository.create(device_id, request.device_name, request.gpio_number)

        # 登録したデバイスの情報を取得
        device = self.repository.find_by_id(device_id)
        if not device:
            logger.error("Failed to create device")
            raise ValueError("Failed to create device")

        logger.info(f"Device registered successfully: {device_id}")
        return DeviceRegisterResponse(
            device_id=device.device_id,
            device_name=device.device_name,
            gpio_number=device.gpio_number,
            created_at=device.created_at,
            updated_at=device.updated_at
        )

    def get_device_list(self) -> List[DeviceDTO]:
        logger.info("Getting device list")
        devices = self.repository.find_all()
        logger.debug(f"Found {len(devices)} devices")
        return [
            DeviceDTO(
                device_id=device.device_id,
                device_name=device.device_name,
                gpio_number=device.gpio_number,
                is_on=gpio_controller.get_status(device.gpio_number),
                created_at=device.created_at,
                updated_at=device.updated_at
            )
            for device in devices
        ]

    def get_device(self, device_id: str) -> DeviceDTO:
        logger.info(f"Getting device: {device_id}")
        device = self.repository.find_by_id(device_id)
        if not device:
            logger.error(f"Device not found: {device_id}")
            raise ValueError(f"Device {device_id} not found")

        return DeviceDTO(
            device_id=device.device_id,
            device_name=device.device_name,
            gpio_number=device.gpio_number,
            is_on=gpio_controller.get_status(device.gpio_number),
            created_at=device.created_at,
            updated_at=device.updated_at
        )

    def turn_on_device(self, device_id: str) -> None:
        logger.info(f"Turning on device: {device_id}")
        device = self.repository.find_by_id(device_id)
        if not device:
            logger.error(f"Device not found: {device_id}")
            raise ValueError(f"Device {device_id} not found")
        
        try:
            gpio_controller.turn_on(device.gpio_number)
            self.repository.update_timestamp(device_id)
            logger.info(f"Device turned on successfully: {device_id}")
        except ValueError as e:
            logger.error(f"Failed to turn on device: {str(e)}")
            raise ValueError(f"Failed to turn on device: {str(e)}")

    def turn_off_device(self, device_id: str) -> None:
        logger.info(f"Turning off device: {device_id}")
        device = self.repository.find_by_id(device_id)
        if not device:
            logger.error(f"Device not found: {device_id}")
            raise ValueError(f"Device {device_id} not found")
        
        try:
            gpio_controller.turn_off(device.gpio_number)
            self.repository.update_timestamp(device_id)
            logger.info(f"Device turned off successfully: {device_id}")
        except ValueError as e:
            logger.error(f"Failed to turn off device: {str(e)}")
            raise ValueError(f"Failed to turn off device: {str(e)}")

    def get_device_status(self, device_id: str) -> bool:
        logger.info(f"Getting device status: {device_id}")
        device = self.repository.find_by_id(device_id)
        if not device:
            logger.error(f"Device not found: {device_id}")
            raise ValueError(f"Device {device_id} not found")
        
        try:
            status = gpio_controller.get_status(device.gpio_number)
            logger.info(f"Device status: {status}")
            return status
        except ValueError as e:
            logger.error(f"Failed to get device status: {str(e)}")
            raise ValueError(f"Failed to get device status: {str(e)}") 
