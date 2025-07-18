import pytest
import uuid
from unittest.mock import Mock, patch
from datetime import datetime
from application.services import ScheduleExecutorService
from application.repositories import DeviceRepository
from hardware.gpio_controller import GPIOController
from infrastructure.models import Device


class TestScheduleExecutorService:
    
    def setup_method(self):
        self.mock_device_repository = Mock(spec=DeviceRepository)
        self.mock_gpio_controller = Mock(spec=GPIOController)
        self.service = ScheduleExecutorService(
            device_repository=self.mock_device_repository,
            gpio_controller=self.mock_gpio_controller
        )
    
    def test_start_scheduler(self):
        """スケジューラーが正常に開始されることを確認"""
        self.service.start()
        assert self.service.scheduler.running is True
    
    def test_add_schedule(self):
        """スケジュールが正常に追加されることを確認"""
        schedule_id = str(uuid.uuid4())
        device_id = str(uuid.uuid4())
        schedule_time = "14:30"
        is_on = True
        
        # デバイス情報をモック
        mock_device = Device(
            device_id=device_id,
            device_name="Test Device",
            gpio_number=18,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.mock_device_repository.find_by_id.return_value = mock_device
        
        self.service.start()
        self.service.add_schedule(schedule_id, device_id, schedule_time, is_on)
        
        # スケジュールが追加されていることを確認
        jobs = self.service.scheduler.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].id == schedule_id
        
        # デバイス情報が取得されていることを確認
        self.mock_device_repository.find_by_id.assert_called_once_with(device_id)
    
    def test_add_schedule_device_not_found(self):
        """存在しないデバイスのスケジュール追加時にエラーが発生することを確認"""
        schedule_id = str(uuid.uuid4())
        device_id = str(uuid.uuid4())
        schedule_time = "14:30"
        is_on = True
        
        # デバイスが見つからない場合
        self.mock_device_repository.find_by_id.return_value = None
        
        self.service.start()
        
        with pytest.raises(ValueError, match="Device not found"):
            self.service.add_schedule(schedule_id, device_id, schedule_time, is_on)
    
    def test_add_schedule_invalid_time_format(self):
        """無効な時刻形式でスケジュール追加時にエラーが発生することを確認"""
        schedule_id = str(uuid.uuid4())
        device_id = str(uuid.uuid4())
        schedule_time = "25:70"  # 無効な時刻
        is_on = True
        
        mock_device = Device(
            device_id=device_id,
            device_name="Test Device",
            gpio_number=18,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.mock_device_repository.find_by_id.return_value = mock_device
        
        self.service.start()
        
        with pytest.raises(ValueError, match="Invalid time format"):
            self.service.add_schedule(schedule_id, device_id, schedule_time, is_on)
    
    def test_remove_schedule(self):
        """スケジュールが正常に削除されることを確認"""
        schedule_id = str(uuid.uuid4())
        device_id = str(uuid.uuid4())
        schedule_time = "14:30"
        is_on = True
        
        # デバイス情報をモック
        mock_device = Device(
            device_id=device_id,
            device_name="Test Device",
            gpio_number=18,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.mock_device_repository.find_by_id.return_value = mock_device
        
        self.service.start()
        self.service.add_schedule(schedule_id, device_id, schedule_time, is_on)
        
        # スケジュールが追加されていることを確認
        jobs = self.service.scheduler.get_jobs()
        assert len(jobs) == 1
        
        # スケジュールを削除
        self.service.remove_schedule(schedule_id)
        
        # スケジュールが削除されていることを確認
        jobs = self.service.scheduler.get_jobs()
        assert len(jobs) == 0
    
    def test_remove_schedule_not_found(self):
        """存在しないスケジュール削除時にエラーが発生することを確認"""
        schedule_id = str(uuid.uuid4())
        
        self.service.start()
        
        with pytest.raises(ValueError, match="Schedule not found"):
            self.service.remove_schedule(schedule_id)
    
    @patch('application.services.logger')
    def test_execute_schedule_success(self, mock_logger):
        """スケジュール実行が成功することを確認"""
        device_id = str(uuid.uuid4())
        gpio_number = 18
        is_on = True
        
        # GPIO制御成功をモック
        self.mock_gpio_controller.turn_on.return_value = None
        
        self.service._execute_schedule(device_id, gpio_number, is_on)
        
        # GPIO制御が呼ばれていることを確認
        self.mock_gpio_controller.turn_on.assert_called_once_with(gpio_number)
        
        # ログが出力されていることを確認
        mock_logger.info.assert_called_once()
    
    @patch('application.services.logger')
    def test_execute_schedule_gpio_failure(self, mock_logger):
        """GPIO制御失敗時にログが出力されることを確認"""
        device_id = str(uuid.uuid4())
        gpio_number = 18
        is_on = True
        
        # デバイス情報をモック（ログ取得用）
        mock_device = Device(
            device_id=device_id,
            device_name="Test Device",
            gpio_number=gpio_number,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.mock_device_repository.find_by_id.return_value = mock_device
        
        # GPIO制御失敗をモック
        self.mock_gpio_controller.turn_on.side_effect = Exception("GPIO control failed")
        
        self.service._execute_schedule(device_id, gpio_number, is_on)
        
        # GPIO制御が呼ばれていることを確認
        self.mock_gpio_controller.turn_on.assert_called_once_with(gpio_number)
        
        # WARNINGログが出力されていることを確認
        mock_logger.warning.assert_called_once()
        warning_call_args = mock_logger.warning.call_args[0][0]
        assert "GPIO control failed" in warning_call_args
        assert "Test Device" in warning_call_args
        assert str(gpio_number) in warning_call_args
    
    def test_execute_schedule_turn_off(self):
        """GPIO OFF制御が正常に動作することを確認"""
        device_id = str(uuid.uuid4())
        gpio_number = 18
        is_on = False
        
        # GPIO制御成功をモック
        self.mock_gpio_controller.turn_off.return_value = None
        
        self.service._execute_schedule(device_id, gpio_number, is_on)
        
        # GPIO OFF制御が呼ばれていることを確認
        self.mock_gpio_controller.turn_off.assert_called_once_with(gpio_number)
    
    def test_parse_time_valid_formats(self):
        """有効な時刻形式が正しくパースされることを確認"""
        # 様々な有効な時刻形式をテスト
        valid_times = ["00:00", "01:30", "12:00", "23:59", "9:05", "14:30"]
        
        for time_str in valid_times:
            hour, minute = self.service._parse_time(time_str)
            assert 0 <= hour <= 23
            assert 0 <= minute <= 59
    
    def test_parse_time_invalid_formats(self):
        """無効な時刻形式でエラーが発生することを確認"""
        invalid_times = ["24:00", "12:60", "abc:def", "12", "12:30:45", ""]
        
        for time_str in invalid_times:
            with pytest.raises(ValueError, match="Invalid time format"):
                self.service._parse_time(time_str)