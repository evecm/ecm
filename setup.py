import shutil
from distutils import dir_util
import sys
import django
import os

root_dir = os.path.abspath(os.path.dirname(__file__))
data_dict = {
    'install_dir': "",
    'vhost_name': "",
    'ip_address': "",
    'port': "",
    'django_dir': os.path.abspath(os.path.dirname(django.__file__)).replace("\\", "/"),
    'src_dir': os.path.join(root_dir, "src").replace("\\", "/"),
    'dist_dir': os.path.join(root_dir, "dist").replace("\\", "/"),
}
sys.path.append(data_dict['src_dir'])
import ecm

def install():

    print "Installing ECM server version %s..." % ecm.get_full_version()

    while data_dict['install_dir'] == "":
        data_dict['install_dir'] = raw_input("ECM install directory? (example: '/var/ECM') ").replace("\\", "/")
    while data_dict['vhost_name'] == "":
        data_dict['vhost_name'] = raw_input("Apache virtual host name? (example: 'ecm.mydomain.com') ")
    while data_dict['ip_address'] == "":
        data_dict['ip_address'] = raw_input("Apache virtual host listen ip address? (example: '*') ")
    while data_dict['port'] == "":
        data_dict['port'] = raw_input("Apache virtual host listen port? (example: '80') ")
    
    print "Django install dir:", data_dict['django_dir']
    
    print "Copying files..."
    dir_util.copy_tree(data_dict['src_dir'], data_dict['install_dir'])

    print "Configuring ECM..."
    vhost_file = os.path.join(data_dict['install_dir'], "ecm-vhost.conf").replace("\\", "/")
    f = open(vhost_file, "r")
    buff = f.read()
    f.close()
    buff %= data_dict
    f = open(vhost_file, "w")
    f.write(buff)
    f.close()
    print
    print "Apache virtual host file '%s' generated. Please include it to your apache configuration." % vhost_file

    settings = os.path.join(data_dict['install_dir'], 'ecm/settings.py').replace("\\", "/")

    print
    print "You can now run 'python manage.py syncdb' to initialize ECM database. Make sure you run the command from '%s'" % data_dict['install_dir']
    print
    print "Note: if needed, you can edit '%s' to configure custom database and email access." % settings

def package():
    if os.path.exists(data_dict['dist_dir']):
        dir_util.remove_tree(data_dict['dist_dir'])
    dist_src =  os.path.join(data_dict['dist_dir'], "src")
    ignore_func = get_ignore_func(os.path.join(root_dir, '.hgignore'))
    shutil.copytree(src=data_dict['src_dir'], dst=dist_src, ignore=ignore_func)
    
    init_file = os.path.join(os.path.join(data_dict['dist_dir'], "src/ecm/__init__.py"))
    timestamp = set_timestamp(init_file)
    version = ecm.version
    
    print version, timestamp
    
    
def get_ignore_func(ignore_file):
    f = open(ignore_file, 'r')
    lines = f.readlines()
    f.close()
    del lines[0] # get rid of the first line, it contains the ignore pattern type
    patterns = []
    for line in lines:
        line = line.strip('\n')
        if line.startswith('src/'):
            line = line[4:]
        patterns.append(line)
    return shutil.ignore_patterns(*patterns)

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
    else:
        print >>sys.stderr, 'Please type "python setup.py install" to install'
        exit(1)
