import logging
from typing import Optional, Tuple
from .pdu import PDU

class GBNReceiver:
    """Go-Back-N接收方实现"""
    
    def __init__(self, udp_socket):
        """
        参数:
            udp_socket: UDP套接字
        """
        self.udp = udp_socket
        self.expected_seq = 1  # 期望接收的序号
        self.logger = logging.getLogger('gbn.receiver')
        self.receive_seq=0  # 记录接收次数

    def receive(self) -> Optional[Tuple[bytes, Tuple[str, int]]]:
        """接收并处理数据包，返回 (数据内容, 源地址)"""
        result = self.udp.receive()
        if result is None:
            #self.logger.debug("接收超时或无数据")
            return None  # 如果没有接收到数据，返回 None

        packet, addr = result
        flag,pdu = PDU.unpack(packet)
        
        if not flag:
            #self.logger.warning("Invalid PDU received (checksum error)")
            status='DataErr'
            self.logger.info(f"RECV seq={self.receive_seq}, pdu_exp={self.expected_seq-1}, pdu_recv={pdu.seq_num}, status={status}")
            return None  # 如果PDU解包失败，返回 None

        # 忽略 ACK 包（作为接收方）
        if pdu.flags & PDU.FLAG_ACK:
            return None

        if pdu.flags & PDU.FLAG_DATA:
            #self.logger.info(f"Received packet seq={pdu.seq_num}, expecting={self.expected_seq}")
            self.receive_seq+=1
            status='OK'
            if pdu.seq_num == self.expected_seq:
                # 正确接收
                self.expected_seq += 1
                self.logger.info(f"RECV seq={self.receive_seq}, pdu_exp={self.expected_seq}, pdu_recv={pdu.seq_num}, status={status}")

                self._send_ack(pdu.seq_num, addr)
                return pdu.data, addr
            else:
                # 序号错误
                status='NoErr'
                self.logger.info(f"RECV seq={self.receive_seq}, pdu_exp={self.expected_seq-1}, pdu_recv={pdu.seq_num}, status={status}")
                self._send_ack(self.expected_seq - 1, addr)
                return None

        return None

    def _send_ack(self, ack_num: int, addr: Tuple[str, int]):
        """发送确认包到指定地址"""
        ack_pdu = PDU(0, ack_num, PDU.FLAG_ACK, b'')
        self.udp.send(ack_pdu.pack(), addr)
        #self.logger.debug(f"Sent ACK for seq={ack_num} to {addr}")
