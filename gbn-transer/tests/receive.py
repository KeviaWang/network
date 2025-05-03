import sys
import os
from pathlib import Path

# 关键修改：将项目根目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import main
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config/host2.ini')
    parser.add_argument('--file', help='要发送的文件',default='test.bin')
    parser.add_argument('--remote', help='远程地址:端口')
    parser.add_argument('--output',help='接收文件保存路径（receive/duplex模式需要）',default='received.txt')
    args = parser.parse_args()
    
    # 模拟命令行参数传递
    sys.argv = ['main.py', '--config', args.config, '--mode', 'receive', '--file', args.file, '--remote', args.remote,'--output',args.output]
    main()