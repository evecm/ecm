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

__date__ = '2012 3 22'
__author__ = 'diabeteman'

import os
from optparse import OptionParser

import ecm
from ecm.lib.subcommand import Subcommand, SubcommandsOptionParser
from ecm.admin.cmd import create, upgrade, control, init, manage



#------------------------------------------------------------------------------
def init_options():
    create_cmd = create.sub_command()
    init_cmd = init.sub_command()
    upgrade_cmd = upgrade.sub_command()
    manage_cmd = manage.sub_command()

    # START - STOP - RESTART
    start_cmd = Subcommand('start',
                           parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                           help='Start an existing ECM instance.',
                           callback=control.start)
    stop_cmd = Subcommand('stop',
                           parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                           help='Stop an existing ECM instance.',
                           callback=control.stop)
    restart_cmd = Subcommand('restart',
                           parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                           help='Restart an existing ECM instance.',
                           callback=control.restart)
    status_cmd = Subcommand('status',
                           parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                           help='Shows the run status of an existing ECM instance.',
                           callback=control.status)

    subcommands = [create_cmd, init_cmd, upgrade_cmd, manage_cmd]
    if not os.name == 'nt':
        # daemonizing processes cannot be done on windows
        subcommands += [start_cmd, stop_cmd, restart_cmd, status_cmd]

    # Set up the global parser and its options.
    return SubcommandsOptionParser(subcommands=subcommands, version=ecm.VERSION)

#------------------------------------------------------------------------------
def run(args=None):
    parser = init_options()
    # Parse the global options and the subcommand options.
    global_options, command, options, args = parser.parse_args(args)
    command.run(command, global_options, options, args)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    run()
