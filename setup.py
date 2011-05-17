from distutils import dir_util
import sys
import django
import os

data_dict = {
    'install_dir': "",
    'vhost_name': "",
    'ip_address': "",
    'port': "",
    'django_dir': os.path.abspath(os.path.dirname(django.__file__)).replace("\\", "/"),
    'root_dir': os.path.abspath(os.path.dirname(__file__)).replace("\\", "/"),
}

def install():

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
    dir_util.copy_tree(os.path.join(data_dict['root_dir'], "src"), data_dict['install_dir'])

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

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'install':
        install()
    else:
        print >>sys.stderr, 'Please type "python setup.py install" to install'
        exit(1)
