import os
from typing import Generator

class FileHandler:
    def __init__(self, chunk_size: int = 1024):
        self.chunk_size = chunk_size
    
    def read_file(self, file_path: str) -> Generator[bytes, None, None]:
        """分块读取文件"""
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except IOError as e:
            raise Exception(f"File read error: {e}")
    
    def write_file(self, file_path: str, data: bytes, mode: str = 'wb'):
        """写入文件"""
        try:
            with open(file_path, mode) as f:
                f.write(data)
        except IOError as e:
            raise Exception(f"File write error: {e}")
    
    def get_file_size(self, file_path: str) -> int:
        """获取文件大小"""
        try:
            return os.path.getsize(file_path)
        except OSError as e:
            raise Exception(f"File size error: {e}")