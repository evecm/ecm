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

__date__ = '2012 3 23'
__author__ = 'diabeteman'

import sys
import socket
from os import path
from ConfigParser import SafeConfigParser
from optparse import OptionParser

from ecm.admin.util import log
from ecm.lib.subcommand import Subcommand
from ecm.admin.cmd import run_server

#-------------------------------------------------------------------------------
def sub_command():
    description = 'Run the embedded server (in the current shell).'
    cmd = Subcommand('run',
                     parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                     help=description, callback=run)
    cmd.parser.description = description
    cmd.parser.add_option('-a', '--access-log',
                          dest='access_log', default=False, action='store_true',
                          help='Display HTTP access log.')
    return cmd

#------------------------------------------------------------------------------
def run(command, global_options, options, args):
    
    if not args:
        command.parser.error('Missing instance directory.')
    instance_dir = args[0]

    config = SafeConfigParser()
    settings_file = path.join(instance_dir, 'settings.ini')
    if not config.read([settings_file]):
        command.parser.error('Settings file "%s" not found.' % settings_file)

    address = config.get('misc', 'server_bind_ip') or '127.0.0.1'
    port = config.getint('misc', 'server_bind_port') or 8888

    log('Starting...')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect( (address, port) )
        log('ERROR: Address "%s:%s" already in use.' % (address, port))
        sys.exit(1)
    except socket.error:
        pass
    finally:
        sock.close()
    log('GEvent WSGI server listening on %s:%s.' % (address, port))
    log('Hit CTRL + C to stop.')
    run_server(instance_dir, address, port, options.access_log)
