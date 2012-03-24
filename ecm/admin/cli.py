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
from ecm.admin.cmd import create, sync, destroy

__date__ = '2012 3 22'
__author__ = 'diabeteman'

from optparse import OptionParser, OptionGroup
from ecm.lib.subcommand import Subcommand, SubcommandsOptionParser

import ecm


DB_ENGINES = {
    'sqlite': 'django.db.backends.sqlite3',
    'mysql': 'django.db.backends.mysql',
    'postgresql': 'django.db.backends.postgresql',
    'postgresql_psycopg2': 'django.db.backends.postgresql_psycopg2'
}
EVE_DB_URL = 'http://eve-corp-management.googlecode.com/files/ECM.EVE.db-3.zip'

def init_options():
    # CREATE
    create_cmd = Subcommand('create',
                            parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                            help='Create a new ECM instance in the given directory.',
                            callback=create.run)
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
    w_group.add_option('--host-name', dest='host_name', default='ecm.example.com',
                       help='The public name of ECM host computer.')
    w_group.add_option('--admin-email', dest='admin_email', default='',
                       help='Email of the server administrator (for error notifications)')
    create_cmd.parser.add_option_group(w_group)


    # SYNC
    sync_cmd = Subcommand('sync',
                          parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                          help='Synchronize an instance\'s database and files.',
                          callback=sync.run)
    sync_cmd.parser.add_option('-n', '--no-syncdb', dest='no_db',
                               help='Do not sync the instance\'s database.',
                               default=False, action='store_true')
    sync_cmd.parser.add_option('-s', '--symlink-files', dest='symlink_files',
                               help='Create symbolic links instead of copying static files.',
                               default=False, action='store_true')

    # DESTROY
    destroy_cmd = Subcommand('destroy',
                             parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                             help='Destroy an existing ECM instance (use with care).',
                             callback=destroy.run)

    # Set up the global parser and its options.
    parser = SubcommandsOptionParser(
        subcommands=(create_cmd, sync_cmd, destroy_cmd),
        version='%s' % ecm.VERSION,
    )

    return parser

def run(args=None):
    parser = init_options()
    # Parse the global options and the subcommand options.
    options, subcommand, suboptions, subargs = parser.parse_args(args)
    print options
    print subcommand
    print suboptions
    print subargs

if __name__ == '__main__':
    run()
