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

__date__ = "2010-01-24"
__author__ = "diabeteman"

import shutil
from distutils import dir_util, archive_util, file_util
import sys
import django
import os
import fnmatch
import tarfile
import re
import tempfile
import subprocess
from django.core import management


root_dir = os.path.abspath(os.path.dirname(__file__))
data_dict = {
    'install_dir': "",
    'vhost_name': "",
    'ip_address': "",
    'port': "",
    'admin_email': "",
    'server_email': "",
    'db_engine': "",
    'db_name': "",
    'db_user': "",
    'db_pass': "",
    'django_dir': os.path.abspath(os.path.dirname(django.__file__)).replace("\\", "/"),
    'src_dir': os.path.join(root_dir, "src").replace("\\", "/"),
    'dist_dir': os.path.join(root_dir, "dist").replace("\\", "/"),
    'package_dir': os.path.join(root_dir, "package").replace("\\", "/"),
}

db_engines = {
    'sqlite': "django.db.backends.sqlite3",
    'mysql': "django.db.backends.mysql",
    'postgresql': "django.db.backends.postgresql",
    'postgresql_psycopg2': "django.db.backends.postgresql_psycopg2"
}

db_settings_old = """'ENGINE': 'django.db.backends.sqlite3',
        'NAME': resolvePath('../db/ECM.db')"""

db_settings_new = """'ENGINE': '%(db_engine)s',
        'NAME': '%(db_name)s',
        'USER': '%(db_user)s',
        'PASSWORD': '%(db_pass)s'"""

sys.path.append(data_dict['src_dir'])
import ecm
FULL_VERSION = ecm.get_full_version()
VERSION = ecm.version
del(sys.modules["ecm"]) 
sys.path.remove(data_dict['src_dir'])

def install():
    print "Installing ECM server version %s..." % FULL_VERSION

    while data_dict['install_dir'] == "":
        data_dict['install_dir'] = raw_input("ECM install directory? (example: '/var/ECM') ").replace("\\", "/")
    while data_dict['vhost_name'] == "":
        data_dict['vhost_name'] = raw_input("Apache virtual host name? (example: 'ecm.mydomain.com') ")
    data_dict['ip_address'] = raw_input("Apache virtual host listen ip address? (default: '*') ")
    if data_dict['ip_address'] == "":
        data_dict['ip_address'] == "*"
    data_dict['port'] = raw_input("Apache virtual host listen port? (default: '80') ")
    if data_dict['port'] == "":
        data_dict['port'] == "80"
    while data_dict['admin_email'] == "":
        data_dict['admin_email'] = raw_input("Email of the server administrator? (for error notifications) ")
    while data_dict['server_email'] == "":
        data_dict['server_email'] = raw_input("Default 'from' email of the server? ")
    while data_dict['db_engine'] not in ('sqlite', 'mysql', 'postgresql', 'postgresql_psycopg2'):
        data_dict['db_engine'] = raw_input("DB engine? (sqlite, mysql, postgresql, postgresql_psycopg2) ")

    if data_dict['db_engine'] != 'sqlite':
        data_dict['db_name'] = raw_input("Database name (default: ecm)? ")
        if data_dict['db_name'] == "":
            data_dict['db_name'] = "ecm"
        data_dict['db_user'] = raw_input("Database user name (default: ecm)? ")
        if data_dict['db_user'] == "":
            data_dict['db_user'] = "ecm"
        data_dict['db_pass'] = raw_input("Database user password (default: ecm)? ")
        if data_dict['db_pass'] == "":
            data_dict['db_pass'] = "ecm"
    
    raw_input("If the installation directory already exists, it will be deleted. "
              "Press 'enter' to proceed with the installation.")
    install_files()
    download_eve_db()
    configure_apache()
    configure_ecm()
    init_ecm_db()
    print
    print "INSTALLATION SUCCESSFUL"
    print
    print "Apache virtual host file '%s' generated. Please include it to your apache configuration." % vhost_file
    print
    print "Note: if needed, you can edit '%s' to change database and email settings." % settings_file.replace("\\", "/")

def upgrade():
    print "Upgrading ECM server to version %s..." % FULL_VERSION
    print "All existing settings will be preserved"
    while data_dict['install_dir'] == "":
        data_dict['install_dir'] = raw_input("ECM install directory? ").replace("\\", "/")
    
    tempdir = tempfile.mkdtemp()
    print "Backuping settings to %s..." % tempdir,
    settings_file = os.path.join(data_dict['install_dir'], "ecm/settings.py")
    vhost_file = os.path.join(data_dict['install_dir'], "ecm.apache.vhost.conf")
    db_folder = os.path.join(data_dict['install_dir'], "db")
    logs_folder = os.path.join(data_dict['install_dir'], "logs")
    if os.path.exists(db_folder): dir_util.copy_tree(db_folder, os.path.join(tempdir, 'db'))
    if os.path.exists(logs_folder): dir_util.copy_tree(logs_folder, os.path.join(tempdir, 'logs'))
    if os.path.exists(settings_file): 
        dir_util.mkpath(os.path.join(tempdir, 'ecm'))
        file_util.copy_file(settings_file, os.path.join(tempdir, 'ecm/settings.py.old'))
    if os.path.exists(vhost_file): file_util.copy_file(vhost_file, tempdir)

    # backup the owner of apache.wsgi
    f_stat = os.stat(os.path.join(data_dict['install_dir'], "apache.wsgi"))

    sys.path.append(data_dict['install_dir'])
    import ecm.settings
    data_dict['db_engine'] = ecm.settings.DATABASES['default']['ENGINE']
    if not data_dict['db_engine'] == db_engines['sqlite']:
        data_dict['db_name'] = ecm.settings.DATABASES['default']['NAME']
        data_dict['db_user'] = ecm.settings.DATABASES['default']['USER']
        data_dict['db_pass'] = ecm.settings.DATABASES['default']['PASSWORD']
    data_dict['admin_email'] = ecm.settings.ADMINS[1]
    data_dict['server_email'] = ecm.settings.DEFAULT_FROM_EMAIL
    data_dict['vhost_name'] = ecm.settings.ECM_BASE_URL
    sys.path.remove(data_dict['install_dir'])
    del(sys.modules["ecm.settings"]) 
    
    print "done"
    install_files()
    dir_util.copy_tree(tempdir, data_dict['install_dir'])
    configure_ecm()
    try:
        print "Restoring file permissions...",
        import stat
        # change owner to backuped owner on installation folder recursively
        for root, dirs, files in os.walk(data_dict['install_dir']):  
            for d in dirs:  
                os.chown(os.path.join(root, d), f_stat.st_uid, f_stat.st_gid)
            for f in files:
                os.chown(os.path.join(root, f), f_stat.st_uid, f_stat.st_gid)
        for s in os.path.join(data_dict['install_dir'], 'scripts'):
            if s[-2:] == 'py':
                os.chmod(s, 0755)
        os.chmod(os.path.join(data_dict['install_dir'], 'ecm/manage.py'), 0755)
        print "done"
    except e:
        print e
    
    print "Deleting temp dir %s..." % tempdir,
    dir_util.remove_tree(tempdir)
    print "done"
    
    answer = None
    while not answer:
        answer = raw_input("Upgrade EVE database? ")
    
    if answer in ['y', 'yes', 'Y']:
        download_eve_db()
    
    migrate_ecm_db()
    
    print
    print "UPGRADE SUCCESSFUL"

def install_files():
    if os.path.exists(data_dict['install_dir']):
        print "Deleting existing files...",
        dir_util.remove_tree(data_dict['install_dir'])
        print "done"
    print "Installing files...",
    dir_util.copy_tree(data_dict['src_dir'], data_dict['install_dir'])
    print "done"
    
def download_eve_db():
    sys.path.append(os.path.join(data_dict['install_dir'], "scripts"))
    import patch_eve_db
    # "Downloading EVE database..."
    options, _ = patch_eve_db.parser.parse_args([])
    patch_eve_db.main(options)

def configure_apache():
    print "Configuring Apache...",
    vhost_file = os.path.join(data_dict['install_dir'], "ecm.apache.vhost.conf").replace("\\", "/")
    f = open(vhost_file, "r")
    buff = f.read()
    f.close()
    buff %= data_dict
    f = open(vhost_file, "w")
    f.write(buff)
    f.close()
    print "done"

def configure_ecm():
    print "Configuring ECM settings...",
    settings_file = os.path.join(data_dict['install_dir'], "ecm/settings.py")
    f = open(settings_file, "r")
    buff = f.read()
    f.close()
    
    if data_dict['db_engine'] in ('mysql', 'postgresql', 'postgresql_psycopg2'):
        data_dict['db_engine'] = db_engines[data_dict['db_engine']]
    if not 'sqlite' in data_dict['db_engine']:
        buff = buff.replace(db_settings_old, db_settings_new % data_dict)
    
    buff = buff.replace("DEBUG = True", "DEBUG = False")
    buff = buff.replace("ADMINS = ()", "ADMINS = ('admin', '%(admin_email)s')" % data_dict)
    buff = buff.replace('DEFAULT_FROM_EMAIL = ""', 'DEFAULT_FROM_EMAIL = "%(server_email)s"' % data_dict)
    buff = buff.replace('ECM_BASE_URL = "127.0.0.1:8000"', 'ECM_BASE_URL = "%(vhost_name)s"' % data_dict)
    
    f = open(settings_file, "w")
    f.write(buff)
    f.close()
    print "done"
    
    
def init_ecm_db():
    print "Initializing database..."
    run_dir = os.path.join(data_dict['install_dir'], 'ecm')
    command = 'python manage.py syncdb --noinput --migrate'
    print '>>>', command
    code = subprocess.call(command, cwd=run_dir)
    if code != 0: raise RuntimeError('Command execution failed') 
    

def migrate_ecm_db():
    print "Migrating database..."
    run_dir = os.path.join(data_dict['install_dir'], 'ecm')
    command = 'python manage.py syncdb --noinput'
    print '>>>', command
    code = subprocess.call(command, cwd=run_dir) # to install south tables
    if code != 0: exit(code)
    # now we must test if SOUTH was already installed/used 
    # in the installation we are migrating
    # we setup Django environment in order to be able to use DB models  
    # and check if there were any existing SOUTH migrations made
    sys.path.append(data_dict['install_dir'])
    import ecm.settings
    management.setup_environ(ecm.settings)
    from south.models import MigrationHistory
    if not MigrationHistory.objects.all():
        # SOUTH has never been used in that installation.
        # we MUST "fake" the first migration, 
        # otherwise the migrate command will fail because DB tables already exist...
        command = 'python manage.py migrate 0001 --all --fake --no-initial-data'
        print '>>>', command
        code = subprocess.call(command, cwd=run_dir)
        if code != 0: exit(code)
    command = 'python manage.py migrate --all --no-initial-data'
    print '>>>', command
    code = subprocess.call(command, cwd=run_dir)
    if code != 0: exit(code)
    del(sys.modules["ecm.settings"]) 
    sys.path.remove(data_dict['install_dir'])

def package():
    if os.path.exists(data_dict['package_dir']):
        print "Removing old package dir..."
        dir_util.remove_tree(data_dict['package_dir'])
    
    package_src_dir =  os.path.join(data_dict['package_dir'], "src")
    print "Copying files to package dir..."
    shutil.copytree(src=data_dict['src_dir'], dst=package_src_dir, ignore=ignore_func)
    shutil.copy(__file__, data_dict['package_dir'])
    print "Inserting timestamp in __init__.py file..."
    init_file = os.path.join(os.path.join(package_src_dir, "ecm/__init__.py"))
    timestamp = set_timestamp(init_file)
    version = VERSION
    print "Version %s.%s" % (version, timestamp)
    
    print "Creating archive..."
    if os.path.exists(data_dict['dist_dir']):
        dir_util.remove_tree(data_dict['dist_dir'])
    dir_util.mkpath(data_dict['dist_dir'])
    archive_name = os.path.normpath("ECM-%s.tar.gz" % version)

    curdir = os.getcwd()
    os.chdir(data_dict['dist_dir'])
    tar = tarfile.open(archive_name, "w:gz")
    tar.add(data_dict['package_dir'], arcname="ECM-%s" % version)
    tar.close()
    os.chdir(curdir)

    print "Archive generated:", archive_name
    
def ignore_func(path, names):
    ignored_names = []
    files = [ os.path.join(path, name) for name in names ]
    for pattern in ['*.pyc', '*.pyo', '*/db/*.db', '*/db/*journal', '*/logs']:
        ignored_names.extend(fnmatch.filter(files, pattern))
    return set([ os.path.basename(name) for name in ignored_names ])

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
    

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'install':
        install()
    elif len(sys.argv) > 1 and sys.argv[1] == 'package':
        package()
    elif len(sys.argv) > 1 and sys.argv[1] == 'upgrade':
        upgrade()
    else:
        print >>sys.stderr, 'usage: "python setup.py {install|upgrade}"'
        exit(1)
