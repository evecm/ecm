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

__date__ = "2011 8 23"
__author__ = "diabeteman"

import django
from os import path
from functions import prompt
from optparse import OptionParser, OptionGroup

#######################################
## CONSTANTS
ROOT_DIR = path.abspath(path.dirname(__file__))

DB_ENGINES = {
    'sqlite': "django.db.backends.sqlite3",
    'mysql': "django.db.backends.mysql",
    'postgresql': "django.db.backends.postgresql",
    'postgresql_psycopg2': "django.db.backends.postgresql_psycopg2"
}


#-------------------------------------------------------------------------------
def parse_args(version, timestamp):

    valid_commands = ['install', 'upgrade', 'package']

    parser = OptionParser(usage='setup.py {%s} [options] [install_dir]' % '|'.join(valid_commands),
                          version="%s.%s" % (version, timestamp))

    parser.add_option("-q", "--quiet", dest="quiet", default=False, action='store_true',
                       help="Do not prompt the user for confirmations (assume 'yes').")
    parser.add_option("-a", "--apache-user", dest="apache_user", default="www-data",
                       help="The user which is running the Apache HTTP deamon. Default is 'www-data'.")

    f_group = OptionGroup(parser, "Folders options")
    f_group.add_option("-s", "--src-dir", dest="src_dir", default=path.join(ROOT_DIR, "src"),
                       help="Source directory where to find the installation files.")
    f_group.add_option("-d", "--dist-dir", dest="dist_dir", default=path.join(ROOT_DIR, "dist"),
                       help="Target directory where to generate the package.")
    f_group.add_option("-j", "--django-dir", dest="django_dir",
                       default=path.abspath(path.dirname(django.__file__)),
                       help="Django installation directory. Default is resolved "
                       "from the interpreter used to run the installation.")
    parser.add_option_group(f_group)

    db_group = OptionGroup(parser, "Database options")
    db_group.add_option("-e", "--database-engine", dest="db_engine",
                        help="DB engine %s" % DB_ENGINES.keys())
    db_group.add_option("-n", "--database-name", dest="db_name", default='ecm',
                        help="Database name (default: ecm)")
    db_group.add_option("-u", "--database-user", dest="db_user", default='ecm',
                        help="Database user (default: ecm)")
    db_group.add_option("-p", "--database-password", dest="db_pass", default='ecm',
                        help="Database user password (default: ecm)")
    db_group.add_option("--eve-db-url", dest="eve_db_url", default='http://eve-corp-management.googlecode.com/files/ECM.EVE.db-1.zip',
                        help="URL where to download EVE database archive.")
    db_group.add_option("--eve-db-zip-archive", dest="eve_zip_archive",
                        help="Local path to EVE database archive.")
    db_group.add_option("--eve-db-file", dest="eve_db_dir",
                        help="Local folder where to extract EVE database file.")
    parser.add_option_group(db_group)

    w_group = OptionGroup(parser, "Web & Mail options")
    w_group.add_option("-H", "--virtual-host-name", dest="vhost_name",
                       help="The name of the Apache virtual host.")
    w_group.add_option("-I", "--listening-ip-address", dest="ip_address", default='*',
                       help="The IP address the virtual host is binded to (default is *).")
    w_group.add_option("-P", "--listening-tcp-port", dest="port", default='80',
                       help="The TCP port the virtual host is binded to (default is 80).")
    w_group.add_option("-A", "--admin-email", dest="admin_email",
                       help="Email of the server administrator (for error notifications)")
    w_group.add_option("-S", "--server-email", dest="server_email",
                       help="'FROM' email address that will be used to send mail to users.")
    w_group.add_option("--smtp-host", dest="smtp_host", default="localhost",
                       help="Name of the SMTP server that will be used to send mail (default: 'localhost').")
    w_group.add_option("--smtp-port", dest="smtp_port", default="25",
                       help="Port of the SMTP server (default: 25).")
    w_group.add_option("--smtp-tls", dest="smtp_tls", default=False, action='store_true',
                       help="Use a secure connection with the SMTP server (default: False).")
    w_group.add_option("--smtp-user", dest="smtp_user", default="",
                       help="User to connect to the SMTP server.")
    w_group.add_option("--smtp-password", dest="smtp_password", default="",
                       help="Password for the SMTP user.")

    parser.add_option_group(w_group)

    options, args = parser.parse_args()

    options.version = version
    options.timestamp = timestamp

    if len(args) == 0:
        parser.error("Missing command {%s}" % '|'.join(valid_commands))
    elif args[0] not in valid_commands:
        parser.error("Unknown command '%s'" % args[0])
    else:
        cmd = args[0]

    if cmd != 'package':
        if len(args) > 1:
            options.install_dir = args[1]
        else:
            options.install_dir = prompt('ECM installation directory?')

    return cmd, options

