import pytest
import os, sys

if __debug__:
    ''' 
    fix ModuleNotFoundError: No module named 'utls'
    add the parent directory to the python path
    or: 
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(base_dir)
    '''
    pythonpath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, pythonpath)

from utls import get_test_case_name, get_error_message, get_test_run_name

class TestUtils:
    json_path = 'test/assets/107135.json'
    
    def test_get_test_run_name(self):
        expected_name = "************"
        result = get_test_run_name(self.json_path)
        assert result == expected_name, f"Expected {expected_name}, but got {result}"
    
    def test_get_test_case_name(self):
        expected_name = "global::J************"
        result = get_test_case_name(self.json_path)
        assert result == expected_name, f"Expected {expected_name}, but got {result}"
        
    def test_get_error_message(self):
        expected_msg = "Assert.Equal() Failure: ************"
        result = get_error_message(self.json_path)
        assert result == expected_msg, f"Expected {expected_msg}, but got {result}"
        
if __name__ == "__main__":
    pytest.main([__file__])