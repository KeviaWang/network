import random
from typing import Tuple

def simulate_error(data: bytes, error_rate: int) -> Tuple[bytes, bool]:
    """模拟数据错误"""
    if random.randint(1, 100) <= error_rate:
        if len(data) > 0:
            pos = random.randint(0, len(data)-1)
            data = bytearray(data)
            data[pos] ^= 0xFF
            return bytes(data), True
    return data, False

def simulate_loss(lost_rate: int) -> bool:
    """模拟丢包"""
    return random.randint(1, 100) <= lost_rate