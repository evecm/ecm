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
from optparse import OptionParser, OptionGroup

import ecm
from ecm.lib.subcommand import Subcommand, SubcommandsOptionParser
from ecm.admin.cmd.create import DB_ENGINES
from ecm.admin.cmd import create, sync, destroy, control



EVE_DB_URL = 'http://eve-corp-management.googlecode.com/files/ECM.EVE.db-3.zip'

#------------------------------------------------------------------------------
def init_options():
    # CREATE
    create_cmd = Subcommand('create',
                            parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                            help='Create a new ECM instance in the given directory.',
                            callback=create.run)

    create_cmd.parser.add_option('-q', '--quiet', dest='quiet',
                                 help='Do not prompt user (use default values).',
                                 default=False, action='store_true')

    db_group = OptionGroup(create_cmd.parser, 'Database options')
    db_group.add_option('--db-engine', dest='db_engine',
                        help='DB engine %s' % DB_ENGINES.keys())
    db_group.add_option('--db-name', dest='db_name',
                        help='Database name')
    db_group.add_option('--db-user', dest='db_user',
                        help='Database user')
    db_group.add_option('--db-password', dest='db_pass',
                        help='Database user password')
    create_cmd.parser.add_option_group(db_group)

    w_group = OptionGroup(create_cmd.parser, 'Web & Mail options')
    w_group.add_option('--host-name', dest='host_name',
                       help='The public name of ECM host computer.')
    w_group.add_option('--admin-email', dest='admin_email',
                       help='Email of the server administrator (for error notifications)')
    w_group.add_option('--server-email', dest='server_email',
                       help='Email used as "from" address in emails sent by the server.')
    create_cmd.parser.add_option_group(w_group)

    server_group = OptionGroup(create_cmd.parser, 'Server options')
    server_group.add_option('--bind-address', dest='bind_address',
                            help='Server listening address')
    server_group.add_option('--bind-port', dest='bind_port',
                            help='Server listening address')
    server_group.add_option('--run-as-user', dest='run_as_user',
                            help='User that will be running the server')
    server_group.add_option('--pid-file', dest='pid_file',
                            help='File where to store the PID of the server process.')
    create_cmd.parser.add_option_group(server_group)

    # SYNC
    sync_cmd = Subcommand('sync',
                          parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                          help='Synchronize an instance\'s database and files.',
                          callback=sync.run)
    sync_cmd.parser.add_option('-n', '--new', dest='new',
                               action='store_true',
                               help='New instance, use django "syncdb".')
    sync_cmd.parser.add_option('--no-migrate', dest='no_migrate',
                               action='store_true',
                               help='Do not modify the instance\'s database.')
    sync_cmd.parser.add_option('-u', '--upgrade-from-1.4.9', dest='upgrade_from_149',
                               action='store_true', default=False,
                               help='Upgrade from ECM-1.4.9.')
    sync_cmd.parser.add_option('--eve-db-url', dest='eve_db_url', default=EVE_DB_URL,
                               help='URL where to download EVE database archive.')
    sync_cmd.parser.add_option('--eve-db-zip-archive', dest='eve_zip_archive',
                               help='Local path to EVE database archive (skips download).')
    sync_cmd.parser.add_option('--skip-eve-db-download', dest='skip_eve_db_download',
                               action='store_true',
                               help='Do NOT download EVE db (use with care).')

    if not os.name == 'nt':
        sync_cmd.parser.add_option('-s', '--symlink-files', dest='symlink_files',
                                   help='Create symbolic links instead of copying static files.',
                                   default=False, action='store_true')

    # DESTROY
    destroy_cmd = Subcommand('destroy',
                             parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                             help='Destroy an existing ECM instance (use with care).',
                             callback=destroy.run)

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

    subcommands = [create_cmd, sync_cmd, destroy_cmd]
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
