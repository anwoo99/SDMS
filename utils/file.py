from utils.config import *

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        raise Exception(f"Error: File not found at {file_path}")
    except json.JSONDecodeError:
        raise Exception(f"Error: Failed to decode JSON from {file_path}")
