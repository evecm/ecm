#!/usr/bin/env python
# Copyright (c) 2010-2011 Robin Jarry
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

__date__ = "2010-05-17"
__author__ = "diabeteman"

import os, sys

scripts_dir = os.path.abspath(os.path.dirname(__file__))
install_dir = os.path.abspath(os.path.join(scripts_dir, "../"))
sys.path.append(install_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ecm.settings'


from ecm import apps, plugins
from ecm.apps.scheduler.validators import extract_function

TASKS = []
for app in apps.LIST:
    TASKS += app.tasks
for plugin in plugins.LIST:
    TASKS += plugin.tasks
TASKS.sort(key=lambda t: t['function'])

def main(task):
    matching_tasks = [ t['function'] for t in TASKS if task in t['function'] ]

    if len(matching_tasks) == 1:
        print 'Executing task: "%s"...' % matching_tasks[0]
        function = extract_function(matching_tasks[0])
        function()
    elif len(matching_tasks) == 0:
        print >>sys.stderr, "No matching tasks for '%s'" % task
        raise IndexError()
    else:
        print >>sys.stderr, "Multiple tasks match for '%s'" % task
        print >>sys.stderr, " ",
        print >>sys.stderr, "\n  ".join(matching_tasks)
        sys.exit(1)

def print_help():
    func_names = [t['function'] for t in TASKS ]
    print >>sys.stderr, "usage: update.py <task>"
    print >>sys.stderr, "with <task> in:\n ",
    print >>sys.stderr, "\n  ".join(func_names)
    print >>sys.stderr
    sys.exit(1)

if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except IndexError:
        print_help()
