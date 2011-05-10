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

_date_ = "2011 4 2"
_author_ = "diabeteman"

from django.db import models
from django.contrib.auth.models import User


class RuleType(models.Model):
    function = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    args = models.CharField(max_length=256)


def get_args(self):
    args = None
    exec(self.args)
    return args

class Rule(models.Model):
    type = models.ForeignKey(RuleType)

class AlertComposition(models.Model):
    alert = models.ForeignKey("Alert")
    rule = models.ForeignKey("Rule")

class AlertSubscription(models.Model):
    user = models.ForeignKey(User)
    alert = models.ForeignKey("Alert")

class Alert(models.Model):
    subscribers = models.ManyToManyField(User, through=AlertSubscription)
    rules = models.ManyToManyField(Rule, through=AlertComposition)
