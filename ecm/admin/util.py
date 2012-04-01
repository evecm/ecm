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

__date__ = '2012 3 25'
__author__ = 'diabeteman'


import os
import sys
import signal
import subprocess

from django.core.management.color import supports_color
from django.utils.termcolors import colorize

#-------------------------------------------------------------------------------
def prompt(message, default_value=None, valid_list=None):
    value = None

    if valid_list is not None:
        list_str = '{%s}' % '|'.join(map(str, valid_list))
        message = '%s %s' % (message, list_str)

    if default_value is not None:
        message = '%s [default=%s]' % (message, default_value)

    if supports_color():
        message = colorize('[ECM] ', fg='cyan', opts=('bold',)) + colorize(message, fg='magenta') + ' '
    else:
        message = '[ECM] ' + message + ' '

    if valid_list is not None:
        while value not in valid_list:
            value = raw_input(message)
            if not value:
                value = default_value
    else:
        while not value:
            value = raw_input(message)
            if not value:
                value = default_value

    return value

#-------------------------------------------------------------------------------
def run_python_cmd(command_line, run_dir, exit_on_failure=True):
    if isinstance(command_line, basestring):
        command_line = command_line.strip().split()

    command_line.insert(0, sys.executable)

    run_command(command_line, run_dir)

#-------------------------------------------------------------------------------
def run_command(command_line, run_dir, exit_on_failure=True):
    if isinstance(command_line, basestring):
        command_line = command_line.strip().split()

    log('$ ' + ' '.join(command_line))
    proc = None
    try:
        proc = subprocess.Popen(command_line, cwd=run_dir, universal_newlines=True)
        exitcode = proc.wait()
        if exitcode != 0 and exit_on_failure:
            sys.exit(exitcode)
    except KeyboardInterrupt:
        if proc is not None:
            os.kill(proc.pid, signal.SIGTERM)

#-------------------------------------------------------------------------------
def log(message, *args):
    message = message % args
    if supports_color():
        print colorize('[ECM] ', fg='cyan', opts=('bold',)) +  message
    else:
        print '[ECM] ' + message

