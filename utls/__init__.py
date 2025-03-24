# coding: utf-8

import logging
import logging.handlers
import logging.config
import yaml
import time
import os
from datetime import datetime
from colorama import Fore, Style

class SensitiveInfoFilter(logging.Filter):
    def filter(self, record):
        if "password" in record.msg:
            record.msg = record.msg.replace("password", "********")
        return True
        
with open('logging_config.yaml', 'r') as f:
    os.makedirs("logs", exist_ok=True)
    config = yaml.safe_load(f)
    config["handlers"]["file"]["filename"] = f'logs/output_{datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")}.log'
    logging.config.dictConfig(config)

logger = logging.getLogger("my_module")
logger.addFilter(SensitiveInfoFilter())

color_mapping = {
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
    "black": Fore.BLACK,
}

def generate_repeated_string(string, times):
    return ''.join([string for _ in range(times)])

def eclapsed_timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"***{func.__name__}*** eclapsed: {end_time - start_time:.4f}seconds")
        return result
    return wrapper

