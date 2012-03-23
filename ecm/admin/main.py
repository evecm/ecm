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

__date__ = '2012 3 22'
__author__ = 'diabeteman'

from optparse import OptionParser, OptionGroup
import ecm
from ecm.admin import install, upgrade

COMMANDS = {
    'install': install.run,
    'upgrade': upgrade.run,
}
DB_ENGINES = {
    'sqlite': 'django.db.backends.sqlite3',
    'mysql': 'django.db.backends.mysql',
    'postgresql': 'django.db.backends.postgresql',
    'postgresql_psycopg2': 'django.db.backends.postgresql_psycopg2'
}
EVE_DB_URL = 'http://eve-corp-management.googlecode.com/files/ECM.EVE.db-3.zip'

def init_options():
    parser = OptionParser(usage='setup.py {%s} [options] [install_dir]' % '|'.join(COMMANDS.keys()),
                          version='%s' % ecm.VERSION)


    parser.add_option('-p', '--plugins', dest='plugins',
                      help='Install or upgrade these plugins. Give the plugins separated '
                           'by commas: "assets,industry,accounting"')

    db_group = OptionGroup(parser, 'Database options')
    db_group.add_option('--database-engine', dest='db_engine',
                        help='DB engine %s' % DB_ENGINES.keys())
    db_group.add_option('--database-name', dest='db_name',
                        help='Database name')
    db_group.add_option('--database-user', dest='db_user',
                        help='Database user')
    db_group.add_option('--database-password', dest='db_pass',
                        help='Database user password')
    db_group.add_option('--eve-db-url', dest='eve_db_url', default=EVE_DB_URL,
                        help='URL where to download EVE database archive.')
    db_group.add_option('--eve-db-zip-archive', dest='eve_zip_archive',
                        help='Local path to EVE database archive.')
    db_group.add_option('--eve-db-file', dest='eve_db_dir',
                        help='Local folder where to extract EVE database file.')
    db_group.add_option('--skip-eve-db-download', dest='skip_eve_db_download',
                        action='store_true', help='Do NOT download EVE db (use with care).')
    parser.add_option_group(db_group)

    w_group = OptionGroup(parser, 'Web & Mail options')
    w_group.add_option('--host-name', dest='host_name',
                       help='The name of ECM host computer.')
    w_group.add_option('--listening-tcp-port', dest='port', type='int', default=80,
                       help='The TCP port the virtual host is binded to (default is 80).')
    w_group.add_option('--admin-email', dest='admin_email',
                       help='Email of the server administrator (for error notifications)')
    w_group.add_option('--server-email', dest='server_email',
                       help='"FROM" email address that will be used to send mail to users.')
    w_group.add_option('--smtp-host', dest='smtp_host', default='localhost',
                       help='Name of the SMTP server that will be used to send mail (default: "localhost").')
    w_group.add_option('--smtp-port', dest='smtp_port', type='int', default=25,
                       help='Port of the SMTP server (default: 25).')
    w_group.add_option('--smtp-tls', dest='smtp_tls', action='store_true', default=False,
                       help='Use a secure connection with the SMTP server (default: False).')
    w_group.add_option('--smtp-user', dest='smtp_user', default='',
                       help='User to connect to the SMTP server.')
    w_group.add_option('--smtp-password', dest='smtp_password', default='',
                       help='Password for the SMTP user.')
    parser.add_option_group(w_group)

    return parser













def run(args=None):
    pass