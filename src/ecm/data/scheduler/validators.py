'''
This file is part of ECM

Created on 9 mars 2011
@author: diabeteman
'''
from django.core.exceptions import ValidationError
import sys, inspect
from django.db import models

    

def extract_function(function_str):
    try:
        module, function = function_str.rsplit('.', 1)
        __import__(module)
        mod = sys.modules[module]
        func = mod.__dict__[function]
        if not inspect.isfunction(func):
            raise UserWarning("'%s.%s' is not a function" % (module, function))
        return func
    except ValueError:
        raise UserWarning("No such module: '%s'" % function_str)
    except ImportError:
        raise UserWarning("No such module '%s' in sys.path" % module)
    except KeyError:
        raise UserWarning("Function '%s' not found in module '%s'" % (module, function))

def extract_model(class_str):
    try:
        module, class_name = class_str.rsplit('.', 1)
        __import__(module)
        mod = sys.modules[module]
        clazz = mod.__dict__[class_name]
        if not (inspect.isclass(clazz) and issubclass(clazz, models.Model)):
            raise UserWarning("'%s.%s' is not a django model" % (module, class_name))
        return clazz
    except ValueError:
        raise UserWarning("No such module: '%s'" % class_str)
    except ImportError:
        raise UserWarning("No such module '%s' in sys.path" % module)
    except KeyError:
        raise UserWarning("Function '%s' not found in module '%s'" % (module, class_name))



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
        except UserWarning as w:
            raise ValidationError(str(w), code=self.code)