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

__date__ = "2010-02-08"
__author__ = "diabeteman"

import sys
import os

#------------------------------------------------------------------------------
def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

#------------------------------------------------------------------------------
def log(msg, *args):
    sys.stdout.write(msg % args)

#------------------------------------------------------------------------------
def logln(msg, *args):
    sys.stdout.write('%s\n' % (msg % args))

#------------------------------------------------------------------------------
def error(msg, *args):
    sys.stderr.write('ERROR: %s\n' % (msg % args))
    sys.exit(1)

#------------------------------------------------------------------------------
def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

#------------------------------------------------------------------------------
def which(program):
    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

