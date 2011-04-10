# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2011-03-09"
__author__ = "diabeteman"



from django.core.exceptions import ValidationError
import sys, inspect
from django.db import models

#------------------------------------------------------------------------------
def extract_function(function_str):
    try:
        module, function = function_str.rsplit('.', 1)
        __import__(module)
        mod = sys.modules[module]
        func = mod.__dict__[function]
        if not inspect.isfunction(func):
            raise ValidationError("'%s.%s' is not a function" % (module, function))
        return func
    except ValueError:
        raise ValidationError("No such module: '%s'" % function_str)
    except ImportError:
        raise ValidationError("No such module '%s' in sys.path" % module)
    except KeyError:
        raise ValidationError("Function '%s' not found in module '%s'" % (module, function))
    
    
#------------------------------------------------------------------------------
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
        extract_function(value)
        

#------------------------------------------------------------------------------
def extract_model(class_str):
    try:
        module, class_name = class_str.rsplit('.', 1)
        __import__(module)
        mod = sys.modules[module]
        clazz = mod.__dict__[class_name]
        if not (inspect.isclass(clazz) and issubclass(clazz, models.Model)):
            raise ValidationError("'%s.%s' is not a django model" % (module, class_name))
        return clazz
    except ValueError:
        raise ValidationError("No such module: '%s'" % class_str)
    except ImportError:
        raise ValidationError("No such module '%s' in sys.path" % module)
    except KeyError:
        raise ValidationError("Model '%s' not found in module '%s'" % (module, class_name))



#------------------------------------------------------------------------------
class ModelValidator:
    message = 'Enter a valid django model'
    code = 'invalid'

    def __init__(self, message='Enter a valid django model', code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
    
    def __call__(self, value):
        """
        Validates that the input matches a django model
        """
        extract_model(value)
        
#------------------------------------------------------------------------------
def extract_args(args_str):
    args = eval(args_str) or {}
    if type(args) != type({}):
        raise ValidationError("args must be a dictionary")
    for key in args.keys():
        if not isinstance(key, basestring):
            raise ValidationError("keys of the args dictionary must be strings")
    return args

#------------------------------------------------------------------------------
class ArgsValidator:
    message = 'Enter a valid arguments dictionary'
    code = 'invalid'

    def __init__(self, message='Enter a valid arguments dictionary', code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
    
    def __call__(self, value):
        """
        Validates that the input matches an arguments dictionary
        """
        extract_args(value)
        
