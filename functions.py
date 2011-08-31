# Copyright (c) 2010-2011 Robin Jarry
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

import sys
from os import path
import fnmatch
import os
from distutils import dir_util, file_util
import subprocess
from django.core import management
import logging
import shlex
import re

__date__ = "2011 8 23"
__author__ = "diabeteman"

#-------------------------------------------------------------------------------
def ignore_func(dir, names):
    ignored_names = []
    files = [ path.join(dir, name) for name in names ]
    for pattern in ['*.pyc', '*.pyo', '*/db/*.db', '*/db/*journal', '*/logs']:
        ignored_names.extend(fnmatch.filter(files, pattern))
    return set([ path.basename(name) for name in ignored_names ])
#-------------------------------------------------------------------------------
def get_timestamp(root_dir):
    sys.path.append(path.join(root_dir, 'src'))
    import ecm
    version = ecm.version
    timestamp = ecm.timestamp
    del(sys.modules["ecm"]) 
    sys.path.remove(path.join(root_dir, 'src'))
    return version, timestamp
#-------------------------------------------------------------------------------
def set_timestamp(file):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    f = open(file, "r")
    buff = f.read()
    f.close()
    buff %= {'timestamp':timestamp}
    f = open(file, "w")
    f.write(buff)
    f.close()
    return timestamp
#-------------------------------------------------------------------------------
def restore_permissions(dir, f_stat):
    # change owner to backuped owner on installation folder recursively
    if not hasattr(os, 'chown'):
        return
    log = get_logger()
    log.info('Restoring owner info on the installation files...')
    os.chown(dir, f_stat.st_uid, f_stat.st_gid)
    for root, dirs, files in os.walk(dir):  
        for d in dirs:  
            d_path = os.path.join(root, d)
            os.chown(d_path, f_stat.st_uid, f_stat.st_gid)
            os.chmod(d_path, 00755)
        for f in files:
            f_path = os.path.join(root, f)
            os.chown(f_path, f_stat.st_uid, f_stat.st_gid)
            os.chmod(f_path, 00644)
    log.info('Owner info restored.')
    log.info('Applying file permissions...')
    for s in os.path.join(dir, 'scripts'):
        if s[-2:] == 'py': 
            os.chmod(os.path.join(dir, s), 00755)
    os.chmod(os.path.join(dir, 'ecm/manage.py'), 00755)
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
    sys.path.append(os.path.join(options.install_dir, "scripts"))
    import patch_eve_db
    opt, _ = patch_eve_db.parser.parse_args([])
    opt.logger = get_logger()
    patch_eve_db.main(opt)


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
def configure_apache(options):
    log = get_logger()
    log.info("Applying configuration to Apache virtual host file...")
    vhost_file = os.path.join(options.install_dir, "ecm.apache.vhost.conf").replace("\\", "/")
    f = open(vhost_file, "r")
    buff = f.read()
    f.close()
    buff %= options.__dict__
    f = open(vhost_file, "w")
    f.write(buff)
    f.close()
    log.info("Apache virtual host file successfully configured.")


#-------------------------------------------------------------------------------
DB_SETTINGS_SQLITE = """'ENGINE': 'django.db.backends.sqlite3',
        'NAME': resolvePath('../db/ECM.db')"""
DB_SETTINGS_OTHER = """'ENGINE': '%(db_engine)s',
        'NAME': '%(db_name)s',
        'USER': '%(db_user)s',
        'PASSWORD': '%(db_pass)s'"""
def configure_ecm(options):
    log = get_logger()
    log.info("Applying configuration to ECM settings.py...")
    settings_file = os.path.join(options.install_dir, "ecm/settings.py")
    f = open(settings_file, "r")
    buff = f.read()
    f.close()
    
    if not 'sqlite' in options.db_engine:
        buff = buff.replace(DB_SETTINGS_SQLITE, DB_SETTINGS_OTHER % options.__dict__)
    
    buff = buff.replace("DEBUG = True", "DEBUG = False")
    buff = buff.replace("ADMINS = ()", 
                        "ADMINS = ('admin', '%(admin_email)s')" % options.__dict__)
    buff = buff.replace('DEFAULT_FROM_EMAIL = ""', 
                        'DEFAULT_FROM_EMAIL = "%(server_email)s"' % options.__dict__)
    buff = buff.replace('ECM_BASE_URL = "127.0.0.1:8000"', 
                        'ECM_BASE_URL = "%(vhost_name)s:%(port)s"' % options.__dict__)
    
    f = open(settings_file, "w")
    f.write(buff)
    f.close()
    log.info("settings.py successfully configured.")

#-------------------------------------------------------------------------------
VHOST_REGEXP = re.compile(r"<VirtualHost (?P<ip_address>[^\s]+):(?P<port>\d+)>")
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

    # backup the owner of apache.wsgi
    file_stat = os.stat(os.path.join(options.install_dir, "apache.wsgi"))
    log.info("Stored the owner info of %s", os.path.join(options.install_dir, "apache.wsgi"))

    vhost_file = os.path.join(options.install_dir, "ecm.apache.vhost.conf")
    with open(vhost_file, 'r') as fd:
        buff = fd.read()
    dic = VHOST_REGEXP.search(buff).groupdict()
    options.ip_address = dic['ip_address']
    options.port = dic['port']


    sys.path.append(options.install_dir)
    import ecm.settings
    options.db_engine = ecm.settings.DATABASES['default']['ENGINE']
    if not 'sqlite' in options.db_engine:
        options.db_name = ecm.settings.DATABASES['default']['NAME']
        options.db_user = ecm.settings.DATABASES['default']['USER']
        options.db_pass = ecm.settings.DATABASES['default']['PASSWORD']
    options.admin_email = ecm.settings.ADMINS[1]
    options.server_email = ecm.settings.DEFAULT_FROM_EMAIL
    options.vhost_name = ecm.settings.ECM_BASE_URL.split(':')[0]
    log.info("Stored configuration from %s", ecm.settings.__file__)
    sys.path.remove(options.install_dir)
    del ecm.settings
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
    
    if not MigrationHistory.objects.all():
        # SOUTH has never been used in that installation.
        # we MUST "fake" the first migration, 
        # otherwise the migrate command will fail because DB tables already exist...
        log.info('First use of South, faking the initial migration...')
        run_command('python manage.py migrate 0001 --all --fake --no-initial-data', run_dir)
    
    run_command('python manage.py migrate --all --no-initial-data', run_dir)

    del(sys.modules["ecm.settings"]) 
    sys.path.remove(options.install_dir)
    log.info('Database Migration successful.')

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

