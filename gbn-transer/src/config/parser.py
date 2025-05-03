import configparser
from typing import Dict, Any

def load_config(config_path: str) -> Dict[str, Any]:
    """加载和解析配置文件"""
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
        
        return {
            'udp_port': config.getint('network', 'udp_port'),
            'data_size': config.getint('network', 'data_size'),
            'error_rate': config.getint('network', 'error_rate'),
            'lost_rate': config.getint('network', 'lost_rate'),
            'window_size': config.getint('network', 'window_size'),
            'timeout': config.getfloat('network', 'timeout'),
            'init_seq_no': config.getint('network', 'init_seq_no'),
            'log_level': config.get('logging', 'level'),
            'log_file': config.get('logging', 'file')
        }
    except Exception as e:
        raise Exception(f"Config parse error: {e}")