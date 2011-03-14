'''
This file is part of ESM

Created on 9 mars 2011
@author: diabeteman
'''
from django.core.exceptions import ValidationError
import sys

    

def extract_function(function_str):
    try:
        module, function = function_str.rsplit('.', 1)
        __import__(module)
        mod = sys.modules[module]
        func = mod.__dict__[function]
        if not callable(func):
            raise UserWarning("'%s.%s' is not a function" % (function, module))
        return func
    except ValueError:
        raise UserWarning("No such module: '%s'" % function_str)
    except ImportError:
        raise UserWarning("No such module '%s' in sys.path" % module)
    except KeyError:
        raise UserWarning("Function '%s' not found in module '%s'" % (function, module))

class FunctionValidator:
    message = 'Enter a valid python function'
    code = 'invalid'

    def __init__(self, message='Enter a valid python function', code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
    
    def __call__(self, value):
        """
        Validates that the input matches a valid function
        """
        try:
            return extract_function(value)
        except UserWarning, w:
            raise ValidationError(str(w), code=self.code)