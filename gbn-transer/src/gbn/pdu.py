import struct
from dataclasses import dataclass
from typing import Optional
from src.file.checksum import calculate_checksum  # 导入校验和计算函数

@dataclass
class PDU:
    """协议数据单元(Protocol Data Unit)"""
    seq_num: int      # 32位序列号
    ack_num: int      # 32位确认号
    flags: int        # 8位控制标志
    data: bytes       # 可变长度数据
    
    # 标志位定义
    FLAG_DATA = 0x01  # 数据包标志
    FLAG_ACK = 0x02   # 确认包标志
    FLAG_SYN = 0x04   # 同步标志
    FLAG_FIN = 0x08   # 结束标志
    
    def pack(self) -> bytes:
        """将PDU打包为字节流"""
        header = struct.pack('!IIB', self.seq_num, self.ack_num, self.flags)
        checksum = calculate_checksum(header + self.data)
        return header + struct.pack('!H', checksum) + self.data
    
    @classmethod
    def unpack(cls, packet: bytes) -> Optional['PDU']:
        """从字节流解包PDU"""
        if len(packet) < 11:  # 最小长度检查(9字节头+2字节校验和)
            return None
            
        header = packet[:9]
        checksum = struct.unpack('!H', packet[9:11])[0]
        data = packet[11:]
        
        # 校验和验证
        seq_num, ack_num, flags = struct.unpack('!IIB', header)
        if checksum != calculate_checksum(header + data):
            return False,cls(seq_num, ack_num, flags, data)
        return True,cls(seq_num, ack_num, flags, data)