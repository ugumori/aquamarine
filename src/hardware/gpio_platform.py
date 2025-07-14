import platform
import os
from log import logger

def is_raspberry_pi() -> bool:
    """Raspberry Pi環境かどうかを判定する"""
    try:
        # /proc/cpuinfoファイルの内容をチェック
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            
            # Raspberry Piの場合にcpuinfoに含まれる文字列をチェック
            raspberry_pi_indicators = ['BCM', 'Raspberry Pi', 'Hardware	: BCM']
            logger.info(f"{cpuinfo}")
            result = any(indicator in cpuinfo for indicator in raspberry_pi_indicators)
            logger.info(f"is_raspberry_pi: {result}")
            return result
        
    except FileNotFoundError:
        # /proc/cpuinfoが存在しない場合（非Linux環境など）
        return False
    except Exception:
        # その他のエラーの場合も安全にFalseを返す
        return False
