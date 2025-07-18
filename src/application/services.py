import uuid
import re
from typing import List
from fastapi import HTTPException
from application.repositories import DeviceRepository, ScheduleRepository
from application.models import (
    DeviceRegisterRequest, DeviceRegisterResponse, DeviceModel,
    DeviceListResponse, DeviceStatusResponse, GPIOStatusResponse,
    DeviceDeleteResponse, DeviceUpdateRequest, DeviceUpdateResponse,
    ScheduleCreateRequest, ScheduleCreateResponse, ScheduleListResponse,
    ScheduleModel
)
from hardware.gpio_controller import GPIOController
from infrastructure.models import Device, Schedule

class DeviceService:
    def __init__(self, device_repository: DeviceRepository, gpio_controller: GPIOController):
        self.device_repository = device_repository
        self.gpio_controller = gpio_controller
    
    def register_device(self, request: DeviceRegisterRequest) -> DeviceRegisterResponse:
        # GPIOが既に使用されているかチェック
        devices = self.device_repository.find_all()
        for device in devices:
            if device.gpio_number == request.gpio_number:
                raise HTTPException(
                    status_code=400,
                    detail=f"GPIO {request.gpio_number} is already in use"
                )
        
        device_id = str(uuid.uuid4())
        self.device_repository.create(device_id, request.device_name, request.gpio_number)
        
        # 作成されたデバイスを取得
        device = self.device_repository.find_by_id(device_id)
        if not device:
            raise HTTPException(status_code=500, detail="Failed to create device")
        
        # GPIOピンを初期化
        self.gpio_controller.setup_pin(request.gpio_number)
        
        return DeviceRegisterResponse(
            device_id=device.device_id,
            device_name=device.device_name,
            gpio_number=device.gpio_number,
            created_at=device.created_at,
            updated_at=device.updated_at
        )
    
    def get_device_list(self) -> DeviceListResponse:
        devices = self.device_repository.find_all()
        device_models = []
        
        for device in devices:
            is_on = self.gpio_controller.get_status(device.gpio_number)
            device_model = DeviceModel(
                device_id=device.device_id,
                device_name=device.device_name,
                gpio_number=device.gpio_number,
                is_on=is_on,
                created_at=device.created_at,
                updated_at=device.updated_at
            )
            device_models.append(device_model)
        
        return DeviceListResponse(devices=device_models)
    
    def get_device_status(self, device_id: str) -> DeviceStatusResponse:
        device = self.device_repository.find_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        is_on = self.gpio_controller.get_status(device.gpio_number)
        
        return DeviceStatusResponse(
            device_id=device.device_id,
            device_name=device.device_name,
            gpio_number=device.gpio_number,
            is_on=is_on
        )
    
    def turn_device_on(self, device_id: str) -> DeviceStatusResponse:
        device = self.device_repository.find_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        self.gpio_controller.turn_on(device.gpio_number)
        self.device_repository.update_timestamp(device_id)
        
        return DeviceStatusResponse(
            device_id=device.device_id,
            device_name=device.device_name,
            gpio_number=device.gpio_number,
            is_on=True
        )
    
    def turn_device_off(self, device_id: str) -> DeviceStatusResponse:
        device = self.device_repository.find_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        self.gpio_controller.turn_off(device.gpio_number)
        self.device_repository.update_timestamp(device_id)
        
        return DeviceStatusResponse(
            device_id=device.device_id,
            device_name=device.device_name,
            gpio_number=device.gpio_number,
            is_on=False
        )
    
    def delete_device(self, device_id: str) -> DeviceDeleteResponse:
        device = self.device_repository.find_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        success = self.device_repository.delete(device_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete device")
        
        return DeviceDeleteResponse(
            message="Device deleted successfully",
            device_id=device_id
        )
    
    def update_device(self, device_id: str, request: DeviceUpdateRequest) -> DeviceUpdateResponse:
        # 更新パラメータが何も指定されていない場合はエラー
        if request.device_name is None and request.gpio_number is None:
            raise HTTPException(status_code=400, detail="No update parameters provided")
        
        # デバイスが存在するかチェック
        device = self.device_repository.find_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # GPIO番号の競合をチェック（GPIO番号が更新される場合のみ）
        if request.gpio_number is not None and request.gpio_number != device.gpio_number:
            devices = self.device_repository.find_all()
            for existing_device in devices:
                if existing_device.gpio_number == request.gpio_number and existing_device.device_id != device_id:
                    raise HTTPException(
                        status_code=400,
                        detail=f"GPIO {request.gpio_number} is already in use"
                    )
        
        # デバイスを更新
        success = self.device_repository.update_device(
            device_id=device_id,
            device_name=request.device_name,
            gpio_number=request.gpio_number
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update device")
        
        # GPIO番号が変更された場合、新しいピンを初期化
        if request.gpio_number is not None and request.gpio_number != device.gpio_number:
            self.gpio_controller.setup_pin(request.gpio_number)
        
        # 更新されたデバイスを取得
        updated_device = self.device_repository.find_by_id(device_id)
        if not updated_device:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated device")
        
        return DeviceUpdateResponse(
            device_id=updated_device.device_id,
            device_name=updated_device.device_name,
            gpio_number=updated_device.gpio_number,
            created_at=updated_device.created_at,
            updated_at=updated_device.updated_at
        )

class GPIOService:
    def __init__(self, gpio_controller: GPIOController):
        self.gpio_controller = gpio_controller
    
    def turn_gpio_on(self, gpio_number: int) -> GPIOStatusResponse:
        self.gpio_controller.turn_on(gpio_number)
        return GPIOStatusResponse(gpio_number=gpio_number, is_on=True)
    
    def turn_gpio_off(self, gpio_number: int) -> GPIOStatusResponse:
        self.gpio_controller.turn_off(gpio_number)
        return GPIOStatusResponse(gpio_number=gpio_number, is_on=False)
    
    def get_gpio_status(self, gpio_number: int) -> GPIOStatusResponse:
        is_on = self.gpio_controller.get_status(gpio_number)
        return GPIOStatusResponse(gpio_number=gpio_number, is_on=is_on)

class ScheduleService:
    def __init__(self, schedule_repository: ScheduleRepository, device_repository: DeviceRepository):
        self.schedule_repository = schedule_repository
        self.device_repository = device_repository
    
    def _validate_time_format(self, time_str: str) -> bool:
        """時間形式（HH:MM）のバリデーション"""
        pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        return re.match(pattern, time_str) is not None
    
    def create_schedule(self, device_id: str, request: ScheduleCreateRequest) -> ScheduleCreateResponse:
        # デバイスが存在するかチェック
        device = self.device_repository.find_by_id(device_id)
        if not device:
            raise HTTPException(status_code=400, detail="Device not found")
        
        # 時間形式のバリデーション
        if not self._validate_time_format(request.schedule):
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM format (00:00-23:59)")
        
        # スケジュールを作成
        schedule_id = str(uuid.uuid4())
        schedule = Schedule(
            schedule_id=schedule_id,
            device_id=device_id,
            schedule=request.schedule,
            is_on=request.is_on
        )
        
        saved_schedule = self.schedule_repository.save(schedule)
        
        return ScheduleCreateResponse(
            schedule_id=saved_schedule.schedule_id,
            device_id=saved_schedule.device_id,
            schedule=saved_schedule.schedule,
            is_on=saved_schedule.is_on,
            created_at=saved_schedule.created_at
        )
    
    def get_schedules_by_device_id(self, device_id: str) -> ScheduleListResponse:
        # デバイスが存在するかチェック
        device = self.device_repository.find_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        schedules = self.schedule_repository.find_by_device_id(device_id)
        schedule_models = []
        
        for schedule in schedules:
            schedule_model = ScheduleModel(
                schedule_id=schedule.schedule_id,
                schedule=schedule.schedule,
                is_on=schedule.is_on
            )
            schedule_models.append(schedule_model)
        
        return ScheduleListResponse(schedules=schedule_models)
    
    def delete_schedule(self, schedule_id: str) -> None:
        # スケジュールが存在するかチェック
        schedule = self.schedule_repository.find_by_id(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        success = self.schedule_repository.delete(schedule_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete schedule")