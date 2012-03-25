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
import sys
from ConfigParser import SafeConfigParser

from django.core import management

from ecm.admin.util import run_python_cmd, get_logger
from ecm.admin.cmd import collect_static_files, download_eve_db


#-------------------------------------------------------------------------------
def migrate_ecm_db(instance_dir, upgrade_from_149=False):
    log = get_logger()
    log.info("Migrating database...")
    run_python_cmd('manage.py syncdb --noinput', instance_dir)

    # now we must test if SOUTH was already installed/used
    # in the installation we are migrating
    # we setup Django environment in order to be able to use DB models
    # and check if there were any existing SOUTH migrations made
    sys.path.append(instance_dir)
    import ecm.settings #@UnresolvedImport
    management.setup_environ(ecm.settings)
    from south.models import MigrationHistory

    if upgrade_from_149:
        # we are upgrading from ECM 1.X.Y, we must perform the init migration
        # on the 'hr' app (rename tables from 'roles_xxxxx' to 'hr_xxxxx')
        MigrationHistory.objects.delete() #@UndefinedVariable
        log.info('Migrating from ECM 1.4.9...')
        run_python_cmd('manage.py migrate hr 0001 --no-initial-data', instance_dir)
    if not MigrationHistory.objects.exclude(app_name='hr'):
        # SOUTH has never been used in that installation.
        # we MUST "fake" the first migration,
        # otherwise the migrate command will fail because DB tables already exist...
        log.info('First use of South, faking the initial migration...')
        run_python_cmd('manage.py migrate 0001 --all --fake --no-initial-data', instance_dir)

    run_python_cmd('manage.py migrate --all --no-initial-data', instance_dir)

    del ecm.settings
    del sys.modules['ecm.settings']
    sys.path.remove(instance_dir)

    log.info('Database Migration successful.')

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

    # run collectstatic
    collect_static_files(instance_dir, options)

    # migrate ecm db
    if not options.no_migrate:
        migrate_ecm_db(instance_dir, options.upgrade_from_149)

    # download eve db
    if not options.skip_eve_db_download:
        download_eve_db(instance_dir,
                        eve_db_dir=sqlite_db_dir,
                        eve_db_url=options.eve_db_url,
                        eve_zip_archive=options.eve_zip_archive)


