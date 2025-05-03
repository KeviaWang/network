import re
from typing import Dict, List
import matplotlib.pyplot as plt
from datetime import datetime

import sys
import os
from pathlib import Path

# 关键修改：将项目根目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))



# 方法1：设置全局字体为黑体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体
plt.rcParams['axes.unicode_minus'] = False    # 正确显示负号

class LogAnalyzer:
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.stats = {
            'total_sent': 0,
            'total_received': 0,
            'timeouts': 0,
            'retransmissions': 0,
            'errors': 0,
            'packet_loss': 0,
            'corrupted_packets': 0,
            'seq_numbers': [],
            'timestamps': []
        }
    
    def analyze(self):
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # 提取时间戳
                timestamp_str = line.split(' - ')[0]
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                self.stats['timestamps'].append(timestamp)
                
                if 'SEND' in line:
                    self.stats['total_sent'] += 1
                    # 提取序列号
                    seq_match = re.search(r'seq=(\d+)', line)
                    if seq_match:
                        self.stats['seq_numbers'].append(int(seq_match.group(1)))
                    if 'status=RT' in line:
                        self.stats['retransmissions'] += 1
                    elif 'status=TO' in line:
                        self.stats['timeouts'] += 1
                elif 'RECV' in line:
                    self.stats['total_received'] += 1
                    if 'status=ERR' in line or 'status=DataErr' in line:
                        self.stats['errors'] += 1
                elif 'TIMEOUT' in line:
                    self.stats['timeouts'] += 1
                elif 'Packet lost' in line:
                    self.stats['packet_loss'] += 1
                elif 'Packet corrupted' in line:
                    self.stats['corrupted_packets'] += 1
        
        return self.stats
    
    def plot_stats(self):
        plt.figure(figsize=(15, 10))
        
        # 统计图表
        plt.subplot(2, 2, 1)
        labels = ['发送', '接收', '重传', '超时', '错误']
        values = [
            self.stats['total_sent'],
            self.stats['total_received'],
            self.stats['retransmissions'],
            self.stats['timeouts'],
            self.stats['errors']
        ]
        plt.bar(labels, values, color=['blue', 'green', 'orange', 'red', 'purple'])
        plt.title('基本传输统计')
        plt.ylabel('数量')
        
        # 丢包和损坏包统计
        plt.subplot(2, 2, 2)
        labels = ['丢包', '损坏包']
        values = [
            self.stats['packet_loss'],
            self.stats['corrupted_packets']
        ]
        plt.bar(labels, values, color=['red', 'yellow'])
        plt.title('网络问题统计')
        plt.ylabel('数量')
        
        # 序列号随时间变化
        plt.subplot(2, 1, 2)
        if len(self.stats['seq_numbers']) > 0:
            plt.plot(self.stats['timestamps'][:len(self.stats['seq_numbers'])], 
                    self.stats['seq_numbers'], 
                    'b-', label='序列号')
            plt.title('序列号随时间变化')
            plt.ylabel('序列号')
            plt.xlabel('时间')
            plt.legend()
            plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('传输统计.png', dpi=300)
        plt.close()

if __name__ == "__main__":
    analyzer = LogAnalyzer("transfer.log")  # 假设日志文件名为gbn.log
    stats = analyzer.analyze()
    print("分析结果:")
    print(f"总发送包数: {stats['total_sent']}")
    print(f"总接收包数: {stats['total_received']}")
    print(f"重传次数: {stats['retransmissions']}")
    print(f"超时次数: {stats['timeouts']}")
    print(f"错误包数: {stats['errors']}")
    print(f"丢包数: {stats['packet_loss']}")
    print(f"损坏包数: {stats['corrupted_packets']}")
    analyzer.plot_stats()