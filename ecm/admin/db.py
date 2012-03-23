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

from django.core import management

from ecm.admin.util import get_logger, run_command

#-------------------------------------------------------------------------------
def init_ecm_db(options):
    log = get_logger()

    log.info("Initializing database...")
    run_dir = os.path.join(options.install_dir, 'ecm')
    run_command(sys.executable + ' manage.py syncdb --noinput --migrate', run_dir)
    log.info('Database initialization successful.')

#-------------------------------------------------------------------------------
def migrate_ecm_db(options):
    log = get_logger()
    log.info("Migrating database...")
    run_dir = os.path.join(options.install_dir, 'ecm')
    run_command(sys.executable + ' manage.py syncdb --noinput', run_dir)

    # now we must test if SOUTH was already installed/used
    # in the installation we are migrating
    # we setup Django environment in order to be able to use DB models
    # and check if there were any existing SOUTH migrations made
    sys.path.append(options.install_dir)
    import ecm.settings
    management.setup_environ(ecm.settings)
    from south.models import MigrationHistory

    if options.old_version.startswith('1.'):
        # we are upgrading from ECM 1.X.Y, we must perform the init migration
        # on the 'hr' app (rename tables from 'roles_xxxxx' to 'hr_xxxxx')
        MigrationHistory.objects.delete() #@UndefinedVariable
        log.info('Migrating from ECM 1.x.y...')
        run_command(sys.executable + ' manage.py migrate 0001 hr --no-initial-data', run_dir)
    if not MigrationHistory.objects.exclude(app_name='hr'):
        # SOUTH has never been used in that installation.
        # we MUST "fake" the first migration,
        # otherwise the migrate command will fail because DB tables already exist...
        log.info('First use of South, faking the initial migration...')
        run_command(sys.executable + ' manage.py migrate 0001 --all --fake --no-initial-data', run_dir)

    run_command(sys.executable + ' manage.py migrate --all --no-initial-data', run_dir)

    del ecm.settings
    del sys.modules['ecm.settings']
    sys.path.remove(options.install_dir)

    log.info('Database Migration successful.')

#-------------------------------------------------------------------------------
def collect_static_files(options):
    log = get_logger()
    log.info("Gathering static files...")
    run_dir = os.path.join(options.install_dir, 'ecm')
    run_command(sys.executable + ' manage.py collectstatic --noinput', run_dir)

#-------------------------------------------------------------------------------
def download_eve_db(options):
    log = get_logger()
    try:
        tempdir = None
        if options.eve_zip_archive is None:
            tempdir = tempfile.mkdtemp()
            options.eve_zip_archive = os.path.join(tempdir, 'EVE.db.zip')
            log.info('Downloading EVE database from %s to %s...', options.eve_db_url, options.eve_zip_archive)
            req = urllib2.urlopen(options.eve_db_url)
            with open(options.eve_zip_archive, 'wb') as fp:
                shutil.copyfileobj(req, fp)
            req.close()
            log.info('Download complete.')

        if options.eve_db_dir is None:
            options.eve_db_dir = path.join(options.install_dir, "db")

        log.info('Expanding %s to %s...', options.eve_zip_archive, options.eve_db_dir)
        zip_file_desc = zipfile.ZipFile(options.eve_zip_archive, 'r')
        for info in zip_file_desc.infolist():
            fname = info.filename
            data = zip_file_desc.read(fname)
            filename = os.path.join(options.eve_db_dir, fname)
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
