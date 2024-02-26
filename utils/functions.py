from .config import *

def check_function_signature(function, expected_args):
    signature = inspect.signature(function)
    function_args = list(signature.parameters.keys())
    
    for expected_arg in expected_args:
        if expected_arg not in function_args:
            raise ValueError(f"Argument '{expected_arg}' is missing in the function signature.")