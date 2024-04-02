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


def dump_data_to_file(data, filename):
    with open(filename, "wb") as f:
        pickle.dump(data, f)

def load_data_from_file(filename):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)
    else:
        return None