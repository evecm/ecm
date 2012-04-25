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
import shutil
from os import path
import subprocess
import signal
from subprocess import PIPE
from optparse import OptionParser
from ConfigParser import SafeConfigParser

from ecm.lib.subcommand import Subcommand
from ecm.admin import instance_template
from ecm.admin.util import run_python_cmd, log
from ecm.admin.cmd import collect_static_files, download_patched_eve_db, patch_ccp_dump,\
    PATCHED_EVE_DB_URL, CCP_EVE_DB_URL

#-------------------------------------------------------------------------------
def sub_command():
    # UPGRADE
    upgrade_cmd = Subcommand('upgrade',
                             parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                             help='Synchronize an instance\'s database and files.',
                             callback=run)
    upgrade_cmd.parser.add_option('--no-syncdb',
                                  dest='no_syncdb', action='store_true', default=False,
                                  help='Do not modify the instance\'s database.')
    upgrade_cmd.parser.add_option('-u', '--upgrade-from-1.4.9',
                                  dest='upgrade_from_149', action='store_true', default=False,
                                  help='Upgrade from ECM-1.4.9.')
    upgrade_cmd.parser.add_option('--eve-db-url',
                                  dest='eve_db_url', default=PATCHED_EVE_DB_URL,
                                  help='URL where to download EVE database archive.')
    upgrade_cmd.parser.add_option('--eve-db-zip-archive',
                                  dest='eve_zip_archive',
                                  help='Local path to EVE database archive (skips download).')
    upgrade_cmd.parser.add_option('--skip-eve-db-download',
                                  dest='skip_eve_db_download', action='store_true',
                                  help='Do NOT download EVE db (use with care).')
    upgrade_cmd.parser.add_option('--from-ccp-dump',
                                  dest='from_ccp_dump', action='store_true', default=False,
                                  help='Update EVE database from CCP official dump (can take a long time).')
    upgrade_cmd.parser.add_option('--ccp-dump-url',
                                  dest='ccp_dump_url', default=CCP_EVE_DB_URL,
                                  help='URL where to download CCP official dump.')
    upgrade_cmd.parser.add_option('--ccp-dump-archive',
                                  dest='ccp_dump_archive',
                                  help='Local archive of CCP official dump (skips download).')
    if not os.name == 'nt':
        upgrade_cmd.parser.add_option('-s', '--symlink-files', dest='symlink_files',
                                      help='Create symbolic links instead of copying static files.',
                                      default=False, action='store_true')

    return upgrade_cmd

#-------------------------------------------------------------------------------
def pipe_to_django_shell(python_code, run_dir, exit_on_failure=True):
    
    log('Piping code to django shell: "%s"' % python_code)
    
    command_line = [sys.executable, 'manage.py', 'shell']
    proc = None
    try:
        proc = subprocess.Popen(command_line, stdin=PIPE, stdout=PIPE, stderr=PIPE, 
                                cwd=run_dir, universal_newlines=True)
        (_, stderr) = proc.communicate(python_code)
        exitcode = proc.wait()
        if exitcode != 0 and exit_on_failure:
            print >>sys.stderr, stderr
            sys.exit(exitcode)
    except KeyboardInterrupt:
        if proc is not None:
            os.kill(proc.pid, signal.SIGTERM)

#-------------------------------------------------------------------------------
def migrate_ecm_db(instance_dir, upgrade_from_149=False):
    instance_dir = path.abspath(instance_dir)
    
    log("Migrating database...")
    run_python_cmd('manage.py syncdb --noinput', instance_dir)

    if upgrade_from_149:
        log('Migrating from ECM 1.4.9...')
        # we are upgrading from ECM 1.X.Y, we must perform the init migration
        # on the 'hr' app (rename tables from 'roles_xxxxx' to 'hr_xxxxx')
        pipe_to_django_shell('from south.models import MigrationHistory;'\
                             'MigrationHistory.objects.all().delete()' , instance_dir)
        
        run_python_cmd('manage.py migrate hr 0001 --noinput', instance_dir)
        # we MUST "fake" the first migration for 1.4.9 apps
        # otherwise the migrate command will fail because DB tables already exist...
        for app in ('common', 'scheduler', 'corp', 'assets', 'accounting'):
            run_python_cmd('manage.py migrate %s 0001 --fake --noinput' % app, instance_dir)

    run_python_cmd('manage.py migrate --all --noinput', instance_dir)
    
    if upgrade_from_149:
        pipe_to_django_shell('from ecm.apps.scheduler.models import ScheduledTask;'\
                             'ScheduledTask.objects.all().delete()' , instance_dir)
        pipe_to_django_shell('from ecm.apps.common.models import UrlPermission;'\
                             'UrlPermission.objects.all().delete()' , instance_dir)

    log('Database Migration successful.')

#-------------------------------------------------------------------------------
def run(command, global_options, options, args):
    if not args:
        command.parser.error('Missing instance directory.')
    instance_dir = args[0]
    sqlite_db_dir = ''
    config = SafeConfigParser()
    if config.read([path.join(instance_dir, 'settings.ini')]):
        sqlite_db_dir = config.get('database', 'sqlite_db_dir')
    if not sqlite_db_dir:
        sqlite_db_dir = path.join(instance_dir, 'db')
    
    # copy ecm_settings.py & manage.py from template
    template_dir = path.abspath(path.dirname(instance_template.__file__))
    shutil.copy(path.join(template_dir, 'settings.py'), instance_dir)
    shutil.copy(path.join(template_dir, 'manage.py'), instance_dir)
    if hasattr(os, 'chmod'):
        os.chmod(path.join(instance_dir, 'manage.py'), 00755)
    
    # run collectstatic
    collect_static_files(instance_dir, options)

    # migrate ecm db
    if not options.no_syncdb:
        migrate_ecm_db(instance_dir, options.upgrade_from_149)

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


