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

__date__ = '2011 8 23'
__author__ = 'diabeteman'

from os import path
from functions import prompt
from optparse import OptionParser, OptionGroup
from ConfigParser import ConfigParser

#######################################
## CONSTANTS
ROOT_DIR = path.abspath(path.dirname(__file__))

DB_ENGINES = {
    'sqlite': 'django.db.backends.sqlite3',
    'mysql': 'django.db.backends.mysql',
    'postgresql': 'django.db.backends.postgresql',
    'postgresql_psycopg2': 'django.db.backends.postgresql_psycopg2'
}

DEFAULT_OPTIONS = {
    'quiet': False,
    'plugins': '',
    'src_dir': path.join(ROOT_DIR, 'src'),
    'dist_dir': path.join(ROOT_DIR, 'dist'),
    
    'db_engine': None,
    'db_name': 'ecm',
    'db_user': 'ecm',
    'db_pass': 'ecm',
    'eve_db_url': 'http://eve-corp-management.googlecode.com/files/ECM.EVE.db-3.zip',
    'eve_zip_archive': None,
    'eve_db_dir': None,
    'skip_eve_db_download': False,
    
    'host_name': None,
    'port': 80,
    'admin_email': None,
    'server_email': None,
    'smtp_host': 'localhost',
    'smtp_port': 25,
    'smtp_tls': False,
    'smtp_user': '',
    'smtp_password': '',
}

#-------------------------------------------------------------------------------
def parse_args(version, timestamp):

    valid_commands = ['install', 'upgrade', 'package', 'clean']

    parser = OptionParser(usage='setup.py {%s} [options] [install_dir]' % '|'.join(valid_commands),
                          version='%s.%s' % (version, timestamp))

    parser.add_option('-q', '--quiet', dest='quiet', action='store_true',
                       help='Do not prompt the user for confirmations (assume "yes").')
    parser.add_option('-p', '--plugins', dest='plugins', 
                      help='Install or upgrade these plugins. Give the plugins separated '
                           'by commas: "assets,industry,accounting"')

    f_group = OptionGroup(parser, 'Folders options')
    f_group.add_option('--src-dir', dest='src_dir', 
                       help='Source directory where to find the installation files.')
    f_group.add_option('--dist-dir', dest='dist_dir', 
                       help='Target directory where to generate the package.')
    parser.add_option_group(f_group)

    db_group = OptionGroup(parser, 'Database options')
    db_group.add_option('--database-engine', dest='db_engine',
                        help='DB engine %s' % DB_ENGINES.keys())
    db_group.add_option('--database-name', dest='db_name',
                        help='Database name (default: ecm)')
    db_group.add_option('--database-user', dest='db_user',
                        help='Database user (default: ecm)')
    db_group.add_option('--database-password', dest='db_pass',
                        help='Database user password (default: ecm)')
    db_group.add_option('--eve-db-url', dest='eve_db_url',
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
    w_group.add_option('--listening-tcp-port', dest='port', type='int', 
                       help='The TCP port the virtual host is binded to (default is 80).')
    w_group.add_option('--admin-email', dest='admin_email',
                       help='Email of the server administrator (for error notifications)')
    w_group.add_option('--server-email', dest='server_email',
                       help='"FROM" email address that will be used to send mail to users.')
    w_group.add_option('--smtp-host', dest='smtp_host',
                       help='Name of the SMTP server that will be used to send mail (default: "localhost").')
    w_group.add_option('--smtp-port', dest='smtp_port', type='int', 
                       help='Port of the SMTP server (default: 25).')
    w_group.add_option('--smtp-tls', dest='smtp_tls', action='store_true',
                       help='Use a secure connection with the SMTP server (default: False).')
    w_group.add_option('--smtp-user', dest='smtp_user',
                       help='User to connect to the SMTP server.')
    w_group.add_option('--smtp-password', dest='smtp_password',
                       help='Password for the SMTP user.')
    parser.add_option_group(w_group)

    cmd_line_options, args = parser.parse_args()

    cmd_line_options.version = version
    cmd_line_options.timestamp = timestamp


    # First, try to read options from "setup.cfg"
    cfgparser = ConfigParser()
    cfgparser.read(path.join(ROOT_DIR, 'setup.cfg'))
    
    default_options = DEFAULT_OPTIONS.copy()
    options_from_file = {}
    for section in cfgparser.sections():
        options_from_file.update(cfgparser.items(section))
    for name, value in options_from_file.items():
        try:
            if value == '':
                # change empty options to None
                value = None
            elif type(eval(value)) in (type(True), type(0), type(None)):
                # cast when possible
                value = eval(value)
        except:
            pass
        
        if value is not None:
            default_options[name] = value
    
    # make sure that command line options override the config file
    for name, value in default_options.items():
        if getattr(cmd_line_options, name) is None:
            setattr(cmd_line_options, name, default_options.get(name, None))
    
    if cmd_line_options.plugins is not None:
        cmd_line_options.plugins = [ 'ecm.plugins.%s' % p for p in cmd_line_options.plugins.split(',') ]
    
    if len(args) == 0:
        parser.error('Missing command {%s}' % '|'.join(valid_commands))
    elif args[0] not in valid_commands:
        parser.error('Unknown command "%s"' % args[0])
    else:
        cmd = args[0]

    if cmd not in  ['package', 'clean']:
        if len(args) > 1:
            cmd_line_options.install_dir = args[1]
        else:
            cmd_line_options.install_dir = prompt('ECM installation directory?')
        cmd_line_options.install_dir = path.normpath(cmd_line_options.install_dir)

    cmd_line_options.src_dir = path.normpath(cmd_line_options.src_dir)
    cmd_line_options.dist_dir = path.normpath(cmd_line_options.dist_dir)

    return cmd, cmd_line_options

