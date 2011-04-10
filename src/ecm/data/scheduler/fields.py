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

__date__ = "2011 4 10"
__author__ = "diabeteman"

from django.db import models
from django.utils.encoding import smart_unicode
from ecm.data.scheduler.validators import FunctionValidator, extract_function, ModelValidator, \
    extract_model, ArgsValidator, extract_args
import inspect


class FunctionField(models.CharField):
    description = "Callable function"
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        models.CharField.__init__(self, *args, **kwargs)
        self.max_length = 256
        self.validators.append(FunctionValidator)
        
    def to_python(self, value):
        if inspect.isfunction(value) or value is None:
            return value
        else:
            return extract_function(value)
    
    def get_prep_value(self, value):
        module = value.__module__
        function = value.__name__
        return smart_unicode(module + "." + function)
    
class ModelField(models.CharField):
    description = "Django model"
    
    def __init__(self, *args, **kwargs):
        models.CharField.__init__(self, *args, **kwargs)
        self.max_length = 256
        self.validators.append(ModelValidator)
        
    def to_python(self, value):
        if inspect.isclass(value) or value is None:
            return value
        else:
            return extract_model(value)
    
    def get_prep_value(self, value):
        module = value.__module__
        model = value.__name__
        return smart_unicode(module + "." + model)

class ArgsField(models.CharField):
    description = "Django model"
    
    def __init__(self, *args, **kwargs):
        models.CharField.__init__(self, *args, **kwargs)
        self.max_length = 256
        self.validators.append(ArgsValidator)
        
    def to_python(self, value):
        if type(value) == type({}) or value is None:
            return value
        else:
            return extract_args(value)
    
    def get_prep_value(self, value):
        return smart_unicode(value)
