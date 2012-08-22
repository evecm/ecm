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

__date__ = "2012 08 09"
__author__ = "Ajurna"

from django.dispatch import Signal, receiver

from ecm.apps.alerts.models import ObserverSpec
from ecm.apps.alerts.observe import observe

###########################################################################
# DEFINED OBSERVER SPECS
OBSERVER_SPECS = [
    {
     "name" : "Alert Task Success Check",
     "description" : "Checks to see if the job completed successfully",
     "handler_function" : "ecm.apps.alerts.views.task",
     "callback_function" : "ecm.apps.alerts.alerts.check_task",
     "arguments_spec" : ["message"],
     "notification_type" : 0,
     },
]

def update_observer_specs(specs):
    """
    Take a list of dicts with observer settings and check they exists
    and are up to date.
    """
    for spec in specs:
        try:
            os = ObserverSpec.objects.get(name = spec['name'])
            
            os.description       = spec['description']
            os.handler_function  = spec['handler_function']
            os.callback_function = spec['callback_function']
            os.arguments_spec    = spec['arguments_spec']
            os.notification_type = spec['notification_type']
        except ObserverSpec.DoesNotExist:
            os = ObserverSpec(name              = spec['name'],
                              description       = spec['description'],
                              handler_function  = spec['handler_function'],
                              callback_function = spec['callback_function'],
                              arguments_spec    = spec['arguments_spec'],
                              notification_type = spec['notification_type']
                              )
            os.save()
update_observer_specs(OBSERVER_SPECS)
###########################################################################
# DEFINED SIGNALS
ALERT_SIGNAL = Signal(providing_args=["message"])


###########################################################################
# DEFINED RECIVERS
@receiver(ALERT_SIGNAL)
def check_alert(sender, **kwargs):
    observe(handler_function=kwargs['task'],
            arguments=kwargs['data'])

###########################################################################
# DEFINED OBSERVER TASKS
def check_task():
    print "check ran"

