from utils.config import *

def check_function_signature(function_list, expected_args):
    for function in function_list:
        signature = inspect.signature(function)
        function_args = list(signature.parameters.keys())
        
        for expected_arg in expected_args:
            if expected_arg not in function_args:
                raise ValueError(f"Argument '{expected_arg}' is missing in the function signature.")
