import uuid
from typing import List

from src.application.repositories import DeviceRepository
from src.hardware.gpio_controller import gpio_controller
from src.application.models import Device as DeviceDTO, DeviceRegisterRequest, DeviceRegisterResponse

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

        device_id, device_name, gpio_number, created_at, updated_at = device
        return DeviceRegisterResponse(
            device_id=device_id,
            device_name=device_name,
            gpio_number=gpio_number,
            created_at=created_at,
            updated_at=updated_at
        )

    def get_device_list(self) -> List[DeviceDTO]:
        devices = self.repository.find_all()
        return [
            DeviceDTO(
                device_id=device_id,
                device_name=device_name,
                gpio_number=gpio_number,
                is_on=gpio_controller.get_status(gpio_number),
                created_at=created_at,
                updated_at=updated_at
            )
            for device_id, device_name, gpio_number, created_at, updated_at in devices
        ]

    def get_device(self, device_id: str) -> DeviceDTO:
        device = self.repository.find_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        device_id, device_name, gpio_number, created_at, updated_at = device
        return DeviceDTO(
            device_id=device_id,
            device_name=device_name,
            gpio_number=gpio_number,
            is_on=gpio_controller.get_status(gpio_number),
            created_at=created_at,
            updated_at=updated_at
        )

    def turn_on_device(self, device_id: str) -> None:
        device = self.repository.find_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        _, _, gpio_number, _, _ = device
        try:
            gpio_controller.turn_on(gpio_number)
            self.repository.update_timestamp(device_id)
        except ValueError as e:
            raise ValueError(f"Failed to turn on device: {str(e)}")

    def turn_off_device(self, device_id: str) -> None:
        device = self.repository.find_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        _, _, gpio_number, _, _ = device
        try:
            gpio_controller.turn_off(gpio_number)
            self.repository.update_timestamp(device_id)
        except ValueError as e:
            raise ValueError(f"Failed to turn off device: {str(e)}")

    def get_device_status(self, device_id: str) -> bool:
        device = self.repository.find_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        _, _, gpio_number, _, _ = device
        try:
            return gpio_controller.get_status(gpio_number)
        except ValueError as e:
            raise ValueError(f"Failed to get device status: {str(e)}") 
