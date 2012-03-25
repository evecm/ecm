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
import tempfile
import urllib2
import zipfile
import shutil
from os import path
from ConfigParser import SafeConfigParser

from django.core import management

from ecm.admin.util import run_python_cmd, get_logger

#-------------------------------------------------------------------------------
def collect_static_files(instance_dir, options):
    log = get_logger()
    log.info("Gathering static files...")
    switches = '--noinput'
    if os.name != 'nt' and options.symlink_files:
        switches += ' --link'
    run_python_cmd('manage.py collectstatic ' + switches, instance_dir)

#-------------------------------------------------------------------------------
def init_ecm_db(instance_dir):
    log = get_logger()
    log.info("Initializing database...")
    run_python_cmd('manage.py syncdb --noinput --migrate', instance_dir)
    log.info('Database initialization successful.')

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
def download_eve_db(instance_dir, eve_db_dir, eve_db_url, eve_zip_archive):
    log = get_logger()
    try:
        tempdir = None
        if eve_zip_archive is None:
            tempdir = tempfile.mkdtemp()
            eve_zip_archive = os.path.join(tempdir, 'EVE.db.zip')
            log.info('Downloading EVE database from %s to %s...', eve_db_url, eve_zip_archive)
            req = urllib2.urlopen(eve_db_url)
            with open(eve_zip_archive, 'wb') as fp:
                shutil.copyfileobj(req, fp)
            req.close()
            log.info('Download complete.')

        if not path.exists(eve_db_dir):
            os.makedirs(eve_db_dir)

        log.info('Expanding %s to %s...', eve_zip_archive, eve_db_dir)
        zip_file_desc = zipfile.ZipFile(eve_zip_archive, 'r')
        for info in zip_file_desc.infolist():
            fname = info.filename
            data = zip_file_desc.read(fname)
            filename = os.path.join(eve_db_dir, fname)
            file_out = open(filename, 'wb')
            file_out.write(data)
            file_out.flush()
            file_out.close()
        zip_file_desc.close()
        log.info('Expansion complete.')
    finally:
        if tempdir is not None:
            log.info('Removing temp files...')
            shutil.rmtree(tempdir)
            log.info('done')

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
    if options.new:
        if 'sqlite' in ecm_db_engine:
            if not os.path.exists(sqlite_db_dir):
                os.makedirs(sqlite_db_dir)
        init_ecm_db(instance_dir)
    elif not options.no_migrate:
        migrate_ecm_db(instance_dir, options.upgrade_from_149)

    # download eve db
    if not options.skip_eve_db_download:
        download_eve_db(instance_dir,
                        eve_db_dir=sqlite_db_dir,
                        eve_db_url=options.eve_db_url,
                        eve_zip_archive=options.eve_zip_archive)


