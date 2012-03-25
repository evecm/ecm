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

from ecm.admin.util import run_python_cmd, get_logger
from ecm.admin.cmd import collect_static_files, download_eve_db

#-------------------------------------------------------------------------------
def init_ecm_db(instance_dir):
    log = get_logger()
    log.info("Initializing database...")
    run_python_cmd('manage.py syncdb --noinput --migrate', instance_dir)
    log.info('Database initialization successful.')

#-------------------------------------------------------------------------------
def run(command, global_options, options, args):
    if not args:
        command.parser.error('Missing instance directory.')
    instance_dir = args[0]
    sqlite_db_dir = ''
    config = SafeConfigParser()
    if config.read([os.path.join(instance_dir, 'settings.ini')]):
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
        download_eve_db(instance_dir,
                        eve_db_dir=sqlite_db_dir,
                        eve_db_url=options.eve_db_url,
                        eve_zip_archive=options.eve_zip_archive)


