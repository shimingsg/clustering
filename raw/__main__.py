# coding: utf-8
from raw import raw

if __name__ == "__main__":
   # Parse command line arguments
   parsed_args = raw.parse_arguments()
   # Generate raw data from JSON files
   raw.generate_raw_data(parsed_args.path_pattern)