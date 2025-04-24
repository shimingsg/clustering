# coding: utf-8

import logging
import logging.config
import yaml
import time
import os
from datetime import datetime
import json

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

logger = logging.getLogger("clustering")
logger.addFilter(SensitiveInfoFilter())

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

def get_error_message(json_path) -> str:
    '''
    Get the error message from the json file.
    
    :param json_path: The path of the json file.
    :return: The error message.
    '''
    return __get_value_from_json(json_path, ['errorMessage'])
        
def get_test_case_name(json_path) -> str:
    '''
    Get the test case name from the json file.
    
    :param json_path: The path of the json file.
    :return: The test case name.
    '''
    return __get_value_from_json(json_path, ['testCase', 'name'])
    
def get_test_run_name(json_path) -> str:
    '''
    Get the test run id from the json file.
    
    :param json_path: The path of the json file.
    :return: The test run id.
    '''
    return __get_value_from_json(json_path, ['testRun','name'])

def __get_value_from_json(json_path, key_path: list) -> str:
    '''
    Retrieve a value from a JSON file based on a key path.
    
    :param json_path: The path of the JSON file.
    :param key_path: A list representing the key path to the desired value.
    :return: The value at the specified key path, or None if not found.
    '''
    try:
        with open(json_path, 'r') as fd:
            test_result = json.load(fd)
            for key in key_path:
                if isinstance(test_result, list):
                    test_result = test_result[0]
                test_result = test_result.get(key, None)
                if test_result is None:
                    return None
            return test_result
    except:
        return None
    
    