import sys
import os
from pathlib import Path

# 关键修改：将项目根目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import main
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config/host1.ini')
    parser.add_argument('--file',  help='要发送的文件',default='test.txt')
    parser.add_argument('--remote', help='远程地址:端口',default='127.0.0.1:8888')
    args = parser.parse_args()
    
    sys.argv = ['main.py', '--config', args.config, '--mode', 'send', '--file', args.file, '--remote', args.remote]
    main()