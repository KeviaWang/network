import time
import logging
import random  
from typing import Dict, Optional, Tuple
from .pdu import PDU

class GBNSender:
    """Go-Back-N发送方实现"""
    
    def __init__(self, udp_socket, window_size: int = 4, timeout: float = 1.0):
        """
        参数:
            udp_socket: UDP套接字
            window_size: 发送窗口大小
            timeout: 超时时间(秒)
        """
        self.udp = udp_socket
        self.window_size = window_size
        self.timeout = timeout
        self.base = 1          # 窗口起始序号
        self.next_seq = 1       # 下一个发送序号
        self.packets: Dict[int, bytes] = {}  # 已发送未确认的包缓存
        self.packets_resend_num={}  # 未确认的包发送次数
        self.timer = None       # 超时定时器
        self.logger = logging.getLogger('gbn.sender')
        self.send_sep=0 # 发送次数编号
        
    def send(self, data: bytes, addr: Tuple[str, int]) -> bool:
        """发送数据并管理窗口"""
        if self.next_seq < self.base + self.window_size:
            pdu = PDU(self.next_seq, 0, PDU.FLAG_DATA, data)
            packet = pdu.pack()
            
            # 模拟网络丢包和错误已在UDPSocket中实现
            self.udp.send(packet, addr)  
            self.packets[self.next_seq] = packet
            self.packets_resend_num[self.next_seq]=1

            # 如果是窗口中的第一个包，启动定时器
            if self.base == self.next_seq:
                self._start_timer()
                
            self.next_seq += 1
            self.send_sep+=1

            self.logger.info(f"SEND seq={self.send_sep}, pdu_to_send={self.next_seq-1}, status={'New'}, ackedNo={self.base-1}")
            #self.logger.info(f"Sent packet seq={self.next_seq-1}")
            return True
        return False  # 窗口已满
        
    def _start_timer(self):
        """启动超时定时器"""
        self.timer = time.time()
    
    def _check_timeout(self) -> bool:
        """检查是否超时"""
        return self.timer and (time.time() - self.timer) >= self.timeout
    
    def handle_ack(self, ack_num: int):
        """处理接收到的确认"""
        if ack_num >= self.base:
            self.base = ack_num + 1  # 滑动窗口
            if self.base == self.next_seq:
                self.timer = None  # 所有包已确认，停止定时器
            else:
                self._start_timer()  # 重启定时器
            self.logger.info(f"Received ACK for seq={ack_num}")
    
    def resend_packets(self, addr: Tuple[str, int]):
        """超时后重传所有未确认的包"""
        #if not self._check_timeout():
            #return
            
        self.logger.warning(f"Timeout, resending window from seq={self.base}")
        for seq in range(self.base, self.next_seq):
            if seq in self.packets:
                self.udp.send(self.packets[seq], addr)
                self.send_sep+=1
                self.packets_resend_num[seq]+=1
                
                if self.packets_resend_num[seq]==2:
                    status='TO'
                else:
                    status='RT'
                self.logger.info(f"SEND seq={self.send_sep}, pdu_to_send={self.next_seq-1}, status={status}, ackedNo={self.base-1}")
        self._start_timer()  # 重启定时器