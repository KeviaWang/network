
import argparse
import logging
import threading
from typing import Dict, Tuple

import sys
import os
from pathlib import Path

# 关键修改：将项目根目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 然后修改所有导入为从src开始的绝对路径
from src.gbn.sender import GBNSender
from src.gbn.receiver import GBNReceiver
from src.gbn.pdu import PDU
from src.file.handler import FileHandler
from src.network.udp import UDPSocket
from src.config.parser import load_config
from src.log.logger import TransferLogger


def setup_logging(config: Dict) -> None:
    """配置日志系统
    
    Args:
        config: 包含日志配置的字典
    """
    logging.basicConfig(
        level=config['log_level'],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config['log_file']),
            logging.StreamHandler()
        ]
    )

def run_sender(config: Dict, file_path: str, remote_addr: Tuple[str, int]) -> None:
    """运行发送方逻辑

    Args:
        config: 配置字典
        file_path: 要发送的文件路径
        remote_addr: (host, port) 形式的远程地址
    """
    udp = None
    try:
        logger = TransferLogger(config)
        udp = UDPSocket(config['udp_port'],
                        config['error_rate'],
                        config['lost_rate'])
        sender = GBNSender(udp,
                           config['window_size'],
                           config['timeout'])
        file_handler = FileHandler(config['data_size'])

        data_generator = file_handler.read_file(file_path) # 分块读取文件
        try:
            current_data = next(data_generator)
        except StopIteration:
            current_data = None

        while current_data is not None or sender.base < sender.next_seq:
            # 1. 只要窗口未满且文件还有内容，就尝试发送
            while current_data is not None and sender.next_seq < sender.base + sender.window_size:
                sender.send(current_data, remote_addr)
                try:
                    current_data = next(data_generator)
                except StopIteration:
                    current_data = None

            # 2. 等待 ACK
            ack_packet = udp.receive(timeout=0.1)
            if ack_packet:
                ack_packet,addr=ack_packet
                unpacked = PDU.unpack(ack_packet)
                if unpacked:
                    flag, pdu = unpacked
                    if flag and (pdu.flags & PDU.FLAG_ACK):
                        sender.handle_ack(pdu.ack_num)
            else:
                # 3. 超时重传
                if sender._check_timeout():
                    sender.resend_packets(remote_addr)

        # 4. 发送结束标志
        fin_pdu = PDU(0, 0, PDU.FLAG_FIN, b'')
        udp.send(fin_pdu.pack(), remote_addr)
        logger.log_send(0, "FIN_SENT", 0)

    except Exception as e:
        logging.error(f"Sender error: {str(e)}")
        raise
    finally:
        if udp:
            udp.close()


def run_receiver(config: Dict, save_path: str) -> None:
    udp = None
    try:
        print(f"【调试】准备绑定端口 {config['udp_port']}...")  # 新增
        udp = UDPSocket(config['udp_port'], 
                       config['error_rate'], 
                       config['lost_rate'])
        print("【调试】Socket创建成功，开始监听...")  # 新增
        
        receiver = GBNReceiver(udp)
        file_handler = FileHandler(config['data_size'])
        logger = TransferLogger(config)
        
        with open(save_path, 'wb') as f:
            while True:
                print("【调试】等待接收数据...")  # 新增
                result = receiver.receive()
        
                # 确保只有在接收到有效数据时才处理
                if result is None:
                    print("【调试】接收超时或无数据")  # 新增
                    continue
                
                data, addr = result
                if data:
                    print(f"【调试】收到有效数据，长度: {len(data)}")  # 新增
                    f.write(data)
                     #  ACK 发送
                    ack_pdu = PDU(
                        seq_num=0,  # 对于ACK包，不需要有效序列号
                        ack_num=receiver.expected_seq - 1,  # 表示已经收到的最后一个
                        flags=PDU.FLAG_ACK,
                        data=b''
                    )
                    udp.send(ack_pdu.pack(), addr)
                    print(f"【调试】已发送ACK: {receiver.expected_seq - 1}")

                # 检查是否收到FIN包
                fin_packet = udp.receive(timeout=0.1)
                if fin_packet:
                    fin_packet,_=fin_packet
                    print("【调试】收到FIN包")  # 新增
                    flag,fin_pdu = PDU.unpack(fin_packet)
                    if flag and (fin_pdu.flags & PDU.FLAG_FIN):
                        logger.log_receive(0, 0, "FIN_RECEIVED")
                        break
                else:
                    print("【调试】FIN包超时")  # 新增超时信息

    except Exception as e:
        print(f"【错误】接收异常: {str(e)}")  # 新增
        logging.error(f"Receiver error: {str(e)}")
        raise
    finally:
        if udp:
            udp.close()
        print("【调试】接收方关闭")  # 新增


def main() -> None:
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description='Go-Back-N 可靠文件传输系统',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # 必需参数
    parser.add_argument('--config', required=True, help='配置文件路径')
    parser.add_argument('--mode', choices=['send', 'receive', 'duplex'], 
                       required=True, help='运行模式')
    
    # 条件参数
    parser.add_argument('--file', help='要发送的文件路径（send/duplex模式需要）')
    parser.add_argument('--output', help='接收文件保存路径（receive/duplex模式需要）')
    parser.add_argument('--remote', help='远程地址，格式 host:port（send/duplex模式需要）')
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = load_config(args.config)
        setup_logging(config)
        
        # 模式路由
        if args.mode == 'send':
            if not all([args.file, args.remote]):
                raise ValueError("发送模式需要 --file 和 --remote 参数")
            host, port = args.remote.split(':')
            run_sender(config, args.file, (host, int(port)))
            
        elif args.mode == 'receive':
            if not args.output:
                raise ValueError("接收模式需要 --output 参数")
            run_receiver(config, args.output)
            
        elif args.mode == 'duplex':
            if not all([args.file, args.output, args.remote]):
                raise ValueError("双工模式需要 --file, --output 和 --remote 参数")
            host, port = args.remote.split(':')
            
            # 启动双线程
            sender_thread = threading.Thread(
                target=run_sender,
                args=(config, args.file, (host, int(port)))
            )
            receiver_thread = threading.Thread(
                target=run_receiver,
                args=(config, args.output)
            )
            
            sender_thread.start()
            receiver_thread.start()
            
            sender_thread.join()
            receiver_thread.join()
    
    except Exception as e:
        logging.critical(f"程序终止: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()