import logging
import time
from typing import Dict

class TransferLogger:
    def __init__(self, config: Dict):
        self.config = config
        self._setup_logging()
    
    def _setup_logging(self):
        
        logging.basicConfig(
            level=self.config['log_level'],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=self.config['log_file'],
            encoding='utf-8'  # 推荐加上编码防止中文乱码
        )
        self.logger = logging.getLogger('gbn.transfer')
    
    def log_send(self, seq: int, status: str, acked: int):
        self.logger.info(f"SEND seq={seq}, status={status}, acked={acked}")
    
    def log_receive(self, exp_seq: int, recv_seq: int, status: str):
        self.logger.info(f"RECV exp={exp_seq}, recv={recv_seq}, status={status}")
    
    def log_timeout(self, seq: int):
        self.logger.warning(f"TIMEOUT seq={seq}")
    
    def log_error(self, msg: str):
        self.logger.error(f"ERROR {msg}")
    
    def log_stats(self, stats: Dict):
        self.logger.info("STATS " + ", ".join(f"{k}={v}" for k, v in stats.items()))