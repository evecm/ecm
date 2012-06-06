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

__date__ = '2012 3 24'
__author__ = 'diabeteman'

from ecm.admin.util import run_python_cmd
from ecm.lib.subcommand import Subcommand, PassThroughOptionParser

#-------------------------------------------------------------------------------
def sub_command():
    description = 'Manage an instance (proxy for manage.py).'
    manage_cmd = Subcommand('manage',
                            parser=PassThroughOptionParser(usage='%prog [OPTIONS] instance_dir'),
                            help=description, callback=run)
    manage_cmd.parser.description = description
    return manage_cmd

#-------------------------------------------------------------------------------
def run(command, global_options, options, args):
    if not args:
        command.parser.error('Missing instance directory.')
    instance_dir = args.pop(0)
    # relay command to manage.py
    run_python_cmd(['manage.py'] + args, run_dir=instance_dir)
