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


from __future__ import with_statement

__date__ = '2012 3 23'
__author__ = 'diabeteman'

import os
from ConfigParser import SafeConfigParser
from optparse import OptionParser

from ecm.admin.util import run_python_cmd, log
from ecm.lib.subcommand import Subcommand
from ecm.admin.cmd import collect_static_files, download_patched_eve_db, PATCHED_EVE_DB_URL,\
    CCP_EVE_DB_URL, patch_ccp_dump

#-------------------------------------------------------------------------------
def sub_command():
    # INIT
    init_cmd = Subcommand('init',
                          parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                          help='Initialize an instance\'s database and files.',
                          callback=run)
    if not os.name == 'nt':
        init_cmd.parser.add_option('-s', '--symlink-files', dest='symlink_files',
                                   help='Create symbolic links instead of copying static files.',
                                   default=False, action='store_true')
    init_cmd.parser.add_option('--eve-db-url',
                               dest='eve_db_url', default=PATCHED_EVE_DB_URL,
                               help='URL where to download EVE database archive.')
    init_cmd.parser.add_option('--eve-db-zip-archive',
                               dest='eve_zip_archive',
                               help='Local path to EVE database archive (skips download).')
    init_cmd.parser.add_option('--skip-eve-db-download',
                               dest='skip_eve_db_download', action='store_true',
                               help='Do NOT download EVE db (use with care).')
    init_cmd.parser.add_option('--from-ccp-dump',
                               dest='from_ccp_dump', action='store_true', default=False,
                               help='Update EVE database from CCP official dump (can take a long time).')
    init_cmd.parser.add_option('--ccp-dump-url',
                               dest='ccp_dump_url', default=CCP_EVE_DB_URL,
                               help='URL where to download CCP official dump.')
    init_cmd.parser.add_option('--ccp-dump-archive',
                               dest='ccp_dump_archive',
                               help='Local archive of CCP official dump (skips download).')
    return init_cmd


#-------------------------------------------------------------------------------
def init_ecm_db(instance_dir):
    log("Initializing database...")
    run_python_cmd('manage.py syncdb --noinput --migrate', instance_dir)
    log('Database initialization successful.')

#-------------------------------------------------------------------------------
def run(command, global_options, options, args):
    if not args:
        command.parser.error('Missing instance directory.')
    instance_dir = args[0]
    sqlite_db_dir = ''
    settings_file = os.path.join(instance_dir, 'settings.ini')
    config = SafeConfigParser()
    if not config.read([settings_file]):
        command.parser.error('Settings file "%s" not found.' % settings_file)
    else:
        sqlite_db_dir = config.get('database', 'sqlite_db_dir')
    if not sqlite_db_dir:
        sqlite_db_dir = os.path.join(instance_dir, 'db')
    ecm_db_engine = config.get('database', 'ecm_engine')

    # run collectstatic
    collect_static_files(instance_dir, options)

    # run syncdb
    if 'sqlite' in ecm_db_engine and not os.path.exists(sqlite_db_dir):
        os.makedirs(sqlite_db_dir)
    init_ecm_db(instance_dir)

    # download eve db
    if not options.skip_eve_db_download:
        if options.from_ccp_dump:
            patch_ccp_dump(ccp_dump_url=options.ccp_dump_url,
                           ccp_dump_archive=options.ccp_dump_archive,
                           eve_db_dir=sqlite_db_dir)
        else:
            download_patched_eve_db(eve_db_url=options.eve_db_url,
                                    eve_zip_archive=options.eve_zip_archive,
                                    eve_db_dir=sqlite_db_dir)


