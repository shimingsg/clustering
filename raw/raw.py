import argparse
import glob
import json
import os, sys
from datetime import datetime
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
from utls import get_error_message, get_test_case_name, get_test_run_name

args = argparse.ArgumentParser()

args.add_argument(
    "--path_pattern",
    "-pp",
    help="The path pattern of the result, e.g. '.\\test\\assets\\*'.",
    type=str,
    default="*.json",
)

parsed_args = args.parse_args()

def generate_raw_data() -> None:
    json_path = parsed_args.path_pattern
    result_json_list = glob.glob(parsed_args.path_pattern, recursive=True)
    # result_json_list = [os.path.abspath(x) for x in result_json_list]
    raw_json_list = []
    for json_path in result_json_list:
        raw_json_list.append(
            {
                "test_case_name": get_test_case_name(json_path),
                "test_run_name": get_test_run_name(json_path),
                "error_message": get_error_message(json_path),
            }
        )
        
    if len(raw_json_list) == 0:
        print("No test result found.")
    else:
        # write the raw json to a file
        if os.path.exists("rawdata") == False:
            os.mkdir("rawdata")
        raw_file_name = f'rawdata/raw_data_{datetime.now().timestamp()}.json'
        with open(raw_file_name, "w") as fd:
            json.dump(raw_json_list, fd, indent=4)
        print(f"Write {len(raw_json_list)} test results to raw.json")
 

if __name__ == "__main__":
    generate_raw_data()
