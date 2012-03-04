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

import sys
import os
import logging
import shlex
import re
import tempfile
import shutil
import urllib2
import zipfile
import fnmatch
import subprocess
from os import path
from distutils import dir_util, file_util
from django.core import management

__date__ = "2011 8 23"
__author__ = "diabeteman"

#-------------------------------------------------------------------------------
def ignore_func(folder, names):
    ignored_names = []
    files = [ path.join(folder, name) for name in names ]
    for pattern in ['*.pyc', '*.pyo', '*/src/db/*', '*/src/logs', '*/src/static']:
        ignored_names.extend(fnmatch.filter(files, pattern))
    return set([ path.basename(name) for name in ignored_names ])

#-------------------------------------------------------------------------------
def prepare_settings(settings_file):
    with open(settings_file, 'r') as f:
        buff = f.read()
    buff = PLUGINS_RE.sub('ECM_PLUGIN_APPS = []', buff)
    with open(settings_file, 'w') as f:
        f.write(buff)
#-------------------------------------------------------------------------------
def get_version(root_dir):
    sys.path.append(path.join(root_dir, 'src'))
    import ecm
    version = ecm.VERSION
    del(sys.modules["ecm"])
    sys.path.remove(path.join(root_dir, 'src'))
    return version
#-------------------------------------------------------------------------------
def set_timestamp(init_file, timestamp):
    f = open(init_file, "r")
    buff = f.read()
    f.close()
    buff %= {'timestamp':timestamp}
    f = open(init_file, "w")
    f.write(buff)
    f.close()
#-------------------------------------------------------------------------------
def restore_permissions(options, f_stat=None):
    # change owner to backuped owner on installation folder recursively
    if not hasattr(os, 'chown'):
        return
    if f_stat is None:
        try:
            import pwd
            userid = pwd.getpwnam(options.apache_user).pw_uid
            groupid = pwd.getpwnam(options.apache_user).pw_gid
        except:
            userid = 0
            groupid = 0
    else:
        userid = f_stat.st_uid
        groupid = f_stat.st_gid
    log = get_logger()
    log.info('Restoring owner info on the installation files...')
    os.chown(options.install_dir, userid, groupid)
    for root, dirs, files in os.walk(options.install_dir):
        for d in dirs:
            d_path = os.path.join(root, d)
            os.chown(d_path, userid, groupid)
            os.chmod(d_path, 00755)
        for f in files:
            f_path = os.path.join(root, f)
            os.chown(f_path, userid, groupid)
            os.chmod(f_path, 00644)
    log.info('Owner info restored.')
    log.info('Applying file permissions...')
    for s in os.path.join(options.install_dir, 'scripts'):
        if s[-2:] == 'py':
            os.chmod(os.path.join(options.install_dir, s), 00755)
    os.chmod(os.path.join(options.install_dir, 'ecm/manage.py'), 00755)
    log.info('Applied file permissions.')
#-------------------------------------------------------------------------------
def prompt(message, valid_list=None):
    value = None
    if valid_list is not None:
        while value not in valid_list:
            value = raw_input('%s %s ' % (message, valid_list))
    else:
        while not value:
            value = raw_input('%s ' % message)
    return value

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

#-------------------------------------------------------------------------------
def install_files(options):
    log = get_logger()
    if os.path.exists(options.install_dir):
        log.info("Deleting existing files...")
        dir_util.remove_tree(options.install_dir)
    log.info("Copying ECM files to installation directory...")
    dir_util.copy_tree(options.src_dir, options.install_dir)
    log.info("Files installation successful.")

#-------------------------------------------------------------------------------
DB_SETTING_RE = re.compile(r"DATABASES.*?'default'\s*:\s*\{[\s\r\n]*(.+?)[\s\r\n]*\},", re.DOTALL)
DB_SETTINGS = """'ENGINE': '%(db_engine)s',
        'NAME': '%(db_name)s',
        'USER': '%(db_user)s',
        'PASSWORD': '%(db_pass)s'"""
PLUGINS_RE = re.compile(r'ECM_PLUGIN_APPS = \[[^\]]*\]', re.DOTALL)
def configure_ecm(options):
    log = get_logger()
    log.info("Applying configuration to ECM settings.py...")
    settings_file = os.path.join(options.install_dir, "ecm/settings.py")
    f = open(settings_file, "r")
    buff = f.read()
    f.close()

    if not 'sqlite' in options.db_engine:
        match = DB_SETTING_RE.search(buff)
        db_str = DB_SETTINGS % options.__dict__
        buff = buff[:match.start(1)] + db_str + buff[match.end(1):]

    buff = buff.replace("DEBUG = True", "DEBUG = False")
    buff = buff.replace("ADMINS = ()",
                        "ADMINS = ('admin', '%(admin_email)s')" % options.__dict__)
    buff = buff.replace('EMAIL_HOST = "localhost"',
                        'EMAIL_HOST = "%(smtp_host)s"' % options.__dict__)
    buff = buff.replace('EMAIL_PORT = ""',
                        'EMAIL_PORT = "%(smtp_port)s"' % options.__dict__)
    buff = buff.replace('EMAIL_USE_TLS = False',
                        'EMAIL_USE_TLS = %(smtp_tls)s' % options.__dict__)
    buff = buff.replace('EMAIL_HOST_USER = ""',
                        'EMAIL_HOST_USER = "%(smtp_user)s"' % options.__dict__)
    buff = buff.replace('EMAIL_HOST_PASSWORD = ""',
                        'EMAIL_HOST_PASSWORD = "%(smtp_password)s"' % options.__dict__)
    buff = buff.replace('DEFAULT_FROM_EMAIL = ""',
                        'DEFAULT_FROM_EMAIL = "%(server_email)s"' % options.__dict__)
    buff = buff.replace('SERVER_EMAIL = ""',
                        'SERVER_EMAIL = "%(server_email)s"' % options.__dict__)
    if options.plugins is not None:
        plugins = 'ECM_PLUGIN_APPS = ['
        for p in options.plugins:
            plugins += '\n    %s,' % repr(p)
        plugins += '\n]'
        buff = buff.replace('ECM_PLUGIN_APPS = []', plugins)
    
    f = open(settings_file, "w")
    f.write(buff)
    f.close()
    log.info("settings.py successfully configured.")

#-------------------------------------------------------------------------------
def backup_settings(options, tempdir):
    log = get_logger()

    log.info("Backuping settings...")
    settings_file = os.path.join(options.install_dir, "ecm/settings.py")

    db_folder = os.path.join(options.install_dir, "db")
    logs_folder = os.path.join(options.install_dir, "logs")
    if os.path.exists(db_folder):
        log.info("Copying %s to %s...", db_folder, tempdir)
        dir_util.copy_tree(db_folder, os.path.join(tempdir, 'db'))
    if os.path.exists(logs_folder):
        log.info("Copying %s to %s...", logs_folder, tempdir)
        dir_util.copy_tree(logs_folder, os.path.join(tempdir, 'logs'))
    if os.path.exists(settings_file):
        dir_util.mkpath(os.path.join(tempdir, 'ecm'))
        log.info("Copying %s to %s...", settings_file, os.path.join(tempdir, 'ecm'))
        file_util.copy_file(settings_file, os.path.join(tempdir, 'ecm/settings.py.old'))

    # backup the owner of settings.py
    file_stat = os.stat(settings_file)
    log.info("Stored the owner info of %s", settings_file)

    sys.path.insert(0, options.install_dir)
    import ecm
    import ecm.settings
    try:
        options.old_version = ecm.VERSION
    except AttributeError:
        # upgrading from ecm 1.x.y
        options.old_version = ecm.version
    options.db_engine = ecm.settings.DATABASES['default']['ENGINE']
    if not 'sqlite' in options.db_engine:
        options.db_name = ecm.settings.DATABASES['default']['NAME']
        options.db_user = ecm.settings.DATABASES['default']['USER']
        options.db_pass = ecm.settings.DATABASES['default']['PASSWORD']
    options.admin_email = ecm.settings.ADMINS[1]
    options.server_email = ecm.settings.DEFAULT_FROM_EMAIL
    try:
        options.plugins = ecm.settings.ECM_PLUGIN_APPS
    except AttributeError:
        # upgrading from ecm 1.x.y we must set default plugins
        options.plugins = [
            'ecm.plugins.accounting',
            'ecm.plugins.assets',
        ]
    log.info("Stored configuration from %s", ecm.settings.__file__)
    sys.path.remove(options.install_dir)
    del ecm
    del ecm.settings
    del(sys.modules["ecm"])
    del(sys.modules["ecm.settings"])

    log.info('All previous settings backuped.')

    return file_stat


#-------------------------------------------------------------------------------
def init_ecm_db(options):
    log = get_logger()
    log.info("Initializing database...")
    run_dir = os.path.join(options.install_dir, 'ecm')
    run_command('python manage.py syncdb --noinput --migrate', run_dir)
    log.info('Database initialization successful.')

#-------------------------------------------------------------------------------
def migrate_ecm_db(options):
    log = get_logger()
    log.info("Migrating database...")
    run_dir = os.path.join(options.install_dir, 'ecm')
    run_command('python manage.py syncdb --noinput', run_dir)

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
        MigrationHistory.objects.delete()
        log.info('Migrating from ECM 1.x.y...')
        run_command('python manage.py migrate 0001 hr --no-initial-data', run_dir)
    if not MigrationHistory.objects.exclude(app_name='hr'):
        # SOUTH has never been used in that installation.
        # we MUST "fake" the first migration,
        # otherwise the migrate command will fail because DB tables already exist...
        log.info('First use of South, faking the initial migration...')
        run_command('python manage.py migrate 0001 --all --fake --no-initial-data', run_dir)

    run_command('python manage.py migrate --all --no-initial-data', run_dir)

    del ecm.settings
    del sys.modules["ecm.settings"]
    sys.path.remove(options.install_dir)
    
    log.info('Database Migration successful.')

#-------------------------------------------------------------------------------
def collect_static_files(options):
    log = get_logger()
    log.info("Gathering static files...")
    run_dir = os.path.join(options.install_dir, 'ecm')
    run_command('python manage.py collectstatic --noinput', run_dir)
    
#-------------------------------------------------------------------------------
def run_command(command_line, run_dir):
    log = get_logger()
    log.info('>>> ' + command_line)
    proc = subprocess.Popen(shlex.split(command_line), cwd=run_dir, bufsize=1, universal_newlines=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = proc.stdout.readline()
        exitcode = proc.poll()
        if (not line) and (exitcode is not None):
            break
        line = line[:-1]
        log.info(line)
    if exitcode != 0:
        sys.exit(exitcode)

#-------------------------------------------------------------------------------

__logger__ = None
def get_logger():
    global __logger__
    if __logger__ is not None:
        return __logger__
    else:
        logfile = path.join(path.abspath(path.dirname(__file__)), 'install.log')
        if path.exists(logfile): os.remove(logfile)
        logger = logging.getLogger()
        file_hdlr = logging.FileHandler(logfile)
        console_hdlr = logging.StreamHandler()
        file_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logger.addHandler(file_hdlr)
        logger.addHandler(console_hdlr)
        logger.setLevel(logging.INFO)
        __logger__ = logger
        return __logger__

