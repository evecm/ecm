#!/usr/bin/env python
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


__date__ = '2010-01-24'
__author__ = 'diabeteman'

import shutil
import shlex
import os
import sys
import tarfile
import tempfile
import subprocess
from distutils import dir_util
from os import path
from optparse import OptionValueError

#-------------------------------------------------------------------------------
def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)
    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

if which('pip') is None and which('pip.exe') is None:
    print >>sys.stderr, 'Please install "pip" and put it in $PATH first.'
    sys.exit(1)
else:
    print >>sys.stderr, 'Checking/installing ECM requirements...',
    ROOT_DIR = path.abspath(path.dirname(__file__))
    command_line = 'pip -q install -r dependencies.txt'
    subprocess.check_call(shlex.split(command_line), cwd=ROOT_DIR)
    print >>sys.stderr, 'all requirements OK'


#-------------------------------------------------------------------------------
import functions
import config


#-------------------------------------------------------------------------------
def install(options):
    log = functions.get_logger()

    log.info('Installing ECM server version %s...', options.version)

    if options.db_engine is not None:
        if options.db_engine not in config.DB_ENGINES.keys():
            raise OptionValueError('DB engine must be one of %s.' % config.DB_ENGINES.keys())
    else:
        options.db_engine = functions.prompt('DB engine?', config.DB_ENGINES.keys())
    options.db_engine = config.DB_ENGINES[options.db_engine]

    if options.host_name is None:
        options.host_name = functions.prompt('ECM host name? (example: ecm.mydomain.com)')

    if options.admin_email is None:
        options.admin_email = functions.prompt('Email of the server administrator? (for error notifications)')

    if options.server_email is None:
        domain = options.host_name.split('.', 1)
        options.server_email = 'ecm.admin@%s' % domain[-1]
    if not options.quiet:
        raw_input('If the installation directory already exists, it will be deleted. '
                  'Press "enter" to proceed with the installation.')
    functions.install_files(options)
    if not options.skip_eve_db_download:
        functions.download_eve_db(options)
    functions.configure_ecm(options)
    functions.restore_permissions(options)
    functions.init_ecm_db(options)
    functions.collect_static_files(options)

    sys.path.insert(0, options.install_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ecm.settings'
    from django.contrib.sites.models import Site
    site, _ = Site.objects.get_or_create(pk=1)
    site.name = options.host_name
    site.domain = options.host_name
    if options.port not in (80, 443):
        site.domain += ':%s' % options.port
    site.save()

    settings_file = os.path.join(options.install_dir, 'ecm/settings.py')
    log.info('\nINSTALLATION SUCCESSFUL\n')
    log.info('If needed, you can edit "%s" to change database and email settings.\n', path.normpath(settings_file))
    log.info('Please see README file for instructions on how to run ECM.\n')

#-------------------------------------------------------------------------------
def upgrade(options):

    log = functions.get_logger()

    log.info('Upgrading ECM server to version %s...', options.version)

    tempdir = tempfile.mkdtemp()
    file_stat = functions.backup_settings(options, tempdir)

    if not options.quiet:
        raw_input('Press "enter" to proceed with the migration.')

    functions.install_files(options)
    dir_util.copy_tree(tempdir, options.install_dir)
    functions.configure_ecm(options)
    if not options.skip_eve_db_download and (options.quiet or
                functions.prompt('Upgrade EVE database?') in ['y', 'yes', 'Y']):
        functions.download_eve_db(options)
    functions.collect_static_files(options)
    functions.restore_permissions(options, file_stat)

    log.info('Deleting temp dir %s...', tempdir)
    dir_util.remove_tree(tempdir)

    functions.migrate_ecm_db(options)

    log.info('')
    log.info('UPGRADE SUCCESSFUL')



#-------------------------------------------------------------------------------
def package(options):
    package_dir = tempfile.mkdtemp()
    try:
        package_src_dir =  os.path.join(package_dir, 'src')
        print 'Copying files to package dir...'
        shutil.copytree(src=options.src_dir, dst=package_src_dir, ignore=functions.ignore_func)

        shutil.copy(path.join(ROOT_DIR, 'functions.py'), package_dir)
        shutil.copy(path.join(ROOT_DIR, 'config.py'), package_dir)
        shutil.copy(path.join(ROOT_DIR, 'setup.cfg'), package_dir)
        shutil.copy(path.join(ROOT_DIR, 'setup.py'), package_dir)
        shutil.copy(path.join(ROOT_DIR, 'LICENSE'), package_dir)
        shutil.copy(path.join(ROOT_DIR, 'README'), package_dir)
        shutil.copy(path.join(ROOT_DIR, 'AUTHORS'), package_dir)
        shutil.copy(path.join(ROOT_DIR, 'dependencies.txt'), package_dir)
        
        print 'Inserting timestamp in __init__.py file...'
        init_file = os.path.join(os.path.join(package_src_dir, 'ecm/__init__.py'))
        options.timestamp = functions.set_timestamp(init_file)
        functions.prepare_settings(os.path.join(package_src_dir, 'ecm/settings.py'))
        print 'Version %s.%s' % (options.version, options.timestamp)

        print 'Creating archive...'
        if os.path.exists(options.dist_dir):
            dir_util.remove_tree(options.dist_dir)
        dir_util.mkpath(options.dist_dir)
        archive_name = os.path.normpath('ECM-%s.tar.gz' % options.version)

        curdir = os.getcwd()
        os.chdir(options.dist_dir)
        tar = tarfile.open(archive_name, 'w:gz')
        def tar_filter(tarinfo):
            tarinfo.uid = tarinfo.gid = 0
            tarinfo.uname = tarinfo.gname = 'root'
            if tarinfo.isdir():
                tarinfo.mode = 00755
            elif tarinfo.isfile():
                _, relpath = tarinfo.path.split('/', 1) 
                if relpath in ('setup.py', 'src/ecm/manage.py'):
                    tarinfo.mode = 00755
                else:
                    tarinfo.mode = 00644
            return tarinfo
        tar.add(package_dir, arcname='ECM-%s' % options.version, filter=tar_filter)
        tar.close()
        os.chdir(curdir)
        print 'Archive generated: %s' % path.join(options.dist_dir, archive_name)
    finally:
        print 'Deleting package dir...'
        dir_util.remove_tree(package_dir)

#-------------------------------------------------------------------------------
def clean(options):
    print 'Deleting "dist" folder...',
    if os.path.exists(options.dist_dir):
        dir_util.remove_tree(options.dist_dir)
    print 'done'

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    version, timestamp = functions.get_timestamp(ROOT_DIR)
    cmd, options = config.parse_args(version, timestamp)

    try:
        if cmd == 'install':
            install(options)
        elif cmd == 'package':
            package(options)
        elif cmd == 'upgrade':
            upgrade(options)
        elif cmd == 'clean':
            clean(options)
    except:
        functions.get_logger().exception('')
        sys.exit(1)
