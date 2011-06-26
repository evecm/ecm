import shutil
from distutils import dir_util, archive_util, file_util
import sys
import django
import os
import fnmatch
import tarfile
import re
import tempfile

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
    'sqlite': "'django.db.backends.sqlite3'",
    'mysql': "'django.db.backends.mysql'",
    'postgresql': "'django.db.backends.postgresql'",
    'postgresql_psycopg2': "'django.db.backends.postgresql_psycopg2'"
}

db_settings_old = re.compile(r"\s*'ENGINE': 'django.db.backends.sqlite3',.*"
                             r"\s*'NAME': resolvePath('../db/ECM.db')", re.DOTALL)

db_settings_new = '''        'ENGINE': %(db_engine)s,
        'NAME': '%(db_name)s',
        'USER': '%(db_user)s',
        'PASSWORD': '%(db_pass)s'
'''

sys.path.append(data_dict['src_dir'])
import ecm

def install():

    print "Installing ECM server version %s..." % ecm.get_full_version()

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
    configure()

def upgrade():
    print "Upgrading ECM server to version %s..." % ecm.get_full_version()
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
    if os.path.exists(settings_file): file_util.copy_file(settings_file, tempdir)
    if os.path.exists(vhost_file): file_util.copy_file(vhost_file, tempdir)
    print "done"
    install_files()
    print "Restoring settings...",
    dir_util.copy_tree(tempdir, data_dict['install_dir'])
    print "done"
    print "Deleting temp dir %s..." % tempdir,
    dir_util.remove_tree(tempdir)
    print "done"
    
    answer = None
    while not answer:
        answer = raw_input("Upgrade EVE database? ")
    
    if answer in ['y', 'yes', 'Y']:
        download_eve_db()

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

def configure():
    print "Configuring ECM...",
    vhost_file = os.path.join(data_dict['install_dir'], "ecm.apache.vhost.conf").replace("\\", "/")
    f = open(vhost_file, "r")
    buff = f.read()
    f.close()
    buff %= data_dict
    f = open(vhost_file, "w")
    f.write(buff)
    f.close()
    
    settings_file = os.path.join(data_dict['install_dir'], "ecm/settings.py")
    f = open(settings_file, "r")
    buff = f.read()
    f.close()
    
    if data_dict['db_engine'] in ('mysql', 'postgresql', 'postgresql_psycopg2'):
        data_dict['db_engine'] = db_engines[data_dict['db_engine']]
        buff = db_settings_old.sub(db_settings_new % data_dict, buff)
    
    buff = buff.replace("DEBUG = True", "DEBUG = False")
    buff = buff.replace("ADMINS = ()", "ADMINS = ('admin', '%(admin_email)s')" % data_dict)
    buff = buff.replace('DEFAULT_FROM_EMAIL = ""', 'DEFAULT_FROM_EMAIL = "%(server_email)s"' % data_dict)
    buff = buff.replace('ECM_BASE_URL = "127.0.0.1:8000"', 'ECM_BASE_URL = "%(vhost_name)s"' % data_dict)
    
    f = open(settings_file, "w")
    f.write(buff)
    f.close()
    print "done"
    print
    print "Apache virtual host file '%s' generated. Please include it to your apache configuration." % vhost_file
    print
    print "You can now run 'python manage.py syncdb' to initialize ECM database. Make sure you run the command from '%s'" % data_dict['install_dir']
    print
    print "Note: if needed, you can edit '%s' to configure custom database and email access." % settings_file.replace("\\", "/")
    


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
    version = ecm.version
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
