from datetime import datetime, UTC
from typing import List, Optional
from application.repositories import DeviceRepository
from hardware.gpio_controller import gpio_controller
from application.models import DeviceDTO, DeviceRegisterRequest, DeviceRegisterResponse
import uuid
import logging

logger = logging.getLogger(__name__)

class DeviceService:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository

    def register_device(self, request: DeviceRegisterRequest) -> DeviceRegisterResponse:
        # GPIOピンが使用中かチェック
        try:
            gpio_controller.setup_pin(request.gpio_number)
        except ValueError as e:
            raise ValueError(f"Failed to register device: {str(e)}")

        # デバイスを登録
        device_id = str(uuid.uuid4())
        self.repository.create(device_id, request.device_name, request.gpio_number)

        # 登録したデバイスの情報を取得
        device = self.repository.find_by_id(device_id)
        if not device:
            raise ValueError("Failed to create device")

        return DeviceRegisterResponse(
            device_id=device.device_id,
            device_name=device.device_name,
            gpio_number=device.gpio_number,
            created_at=device.created_at,
            updated_at=device.updated_at
        )

    def get_device_list(self) -> List[DeviceDTO]:
        devices = self.repository.find_all()
        logger.debug(f"devices: {devices}")
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
        device = self.repository.find_by_id(device_id)
        if not device:
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
        device = self.repository.find_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        try:
            gpio_controller.turn_on(device.gpio_number)
            self.repository.update_timestamp(device_id)
        except ValueError as e:
            raise ValueError(f"Failed to turn on device: {str(e)}")

    def turn_off_device(self, device_id: str) -> None:
        device = self.repository.find_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        try:
            gpio_controller.turn_off(device.gpio_number)
            self.repository.update_timestamp(device_id)
        except ValueError as e:
            raise ValueError(f"Failed to turn off device: {str(e)}")

    def get_device_status(self, device_id: str) -> bool:
        device = self.repository.find_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        try:
            return gpio_controller.get_status(device.gpio_number)
        except ValueError as e:
            raise ValueError(f"Failed to get device status: {str(e)}") 
