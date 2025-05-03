import socket
import random
import logging
from typing import Optional, Tuple

class UDPSocket:
    """UDP套接字封装，支持错误模拟"""
    
    def __init__(self, port: int, error_rate: int = 0, lost_rate: int = 0):
        """
        参数:
            port: 绑定端口
            error_rate: 错误率百分比(0-100)
            lost_rate: 丢包率百分比(0-100)
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        self.error_rate = error_rate
        self.lost_rate = lost_rate
        self.logger = logging.getLogger('network.udp')


    def send(self, data: bytes, addr: Tuple[str, int]):
        """发送数据包，模拟可能的错误和丢包"""
        if self._simulate_loss():
            self.logger.debug(f"Packet lost (simulated), dest={addr}")
            return
            
        if self._simulate_error():
            data = self._corrupt_data(data)
            self.logger.debug(f"Packet corrupted (simulated), dest={addr}")
            
        self.sock.sendto(data, addr)
    
    def receive(self, timeout: float = None) :
        if timeout:
            self.sock.settimeout(timeout)
        try:
            #print(f"【网络层】准备接收数据（超时:{timeout}s）...")  # 新增
            data, addr = self.sock.recvfrom(4096)
            #print(f"【网络层】收到来自 {addr} 的数据，长度: {len(data)}")  # 新增
            return data,addr
        except socket.timeout:
            #print("【网络层】接收超时")  # 新增
            return None
        except Exception as e:
            #print(f"【网络层】接收错误: {str(e)}")  # 新增
            self.logger.error(f"Receive error: {e}")
            return None
    
    def close(self):
        """关闭socket"""
        self.sock.close()
    
    def _simulate_loss(self) -> bool:
        """模拟丢包"""
        return random.randint(1, 100) <= self.lost_rate
    
    def _simulate_error(self) -> bool:
        """模拟数据错误"""
        return random.randint(1, 100) <= self.error_rate
    
    def _corrupt_data(self, data: bytes) -> bytes:
        """随机破坏一个字节"""
        if len(data) == 0:
            return data
        pos = random.randint(0, len(data)-1)
        corrupted = bytearray(data)
        corrupted[pos] ^= 0xFF
        return bytes(corrupted)