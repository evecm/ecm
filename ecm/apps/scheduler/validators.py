# Copyright (c) 2010-2012 Robin Jarry
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

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
        raise ValidationError("Function '%s' not found in module '%s'" % (function, module))


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
        if not hasattr(clazz, 'DATE_FIELD'):
            raise ValidationError("Model '%s.%s' does not have a 'DATE_FIELD' attribute" % (module, class_name))
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

