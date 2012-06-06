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

__date__ = '2012 3 24'
__author__ = 'diabeteman'

import os
import sys
import time
import socket
from os import path
from ConfigParser import SafeConfigParser
from optparse import OptionParser

from ecm.admin.cmd import run_server
from ecm.admin.util import log
from ecm.lib.subcommand import Subcommand
from ecm.lib.daemon import Daemon

#------------------------------------------------------------------------------
def sub_command():
    description = 'Control the embedded daemon server of an existing ECM instance.'
    cmd = Subcommand('start', aliases=('stop', 'restart', 'status'),
                     parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                     help=description, callback=run)
    cmd.parser.description = description
    cmd.parser.add_option('-l', '--log-file',
                          dest='logfile', metavar='FILE',
                          help='Write server access log to FILE. Default is "/dev/null".')
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

    pidfile = config.get('misc', 'pid_file') or 'ecm.pid'
    address = config.get('misc', 'server_bind_ip') or '127.0.0.1'
    port = config.getint('misc', 'server_bind_port') or 8888
    run_as_user = config.get('misc', 'run_as_user') or None

    if not path.isabs(pidfile):
        pidfile = path.abspath(path.join(instance_dir, pidfile))

    real_command = sys.argv[1]

    if real_command == 'status':
        if path.isfile(pidfile):
            with open(pidfile, 'r') as pf:
                pid = pf.read()
            log('Instance is running with PID: %s' % pid.strip())
        else:
            log('Instance is stopped')
        sys.exit(0)
    else:
        if run_as_user:
            import pwd #@UnresolvedImport
            try:
                uid = pwd.getpwnam(run_as_user).pw_uid
            except KeyError:
                command.parser.error('User "%s" does not exist.' % run_as_user)
        else:
            uid = None

        if options.logfile is not None:
            logfile = path.abspath(options.logfile)
            logdir = path.dirname(logfile)
            if not path.exists(logdir):
                os.makedirs(logdir)
        else:
            logfile = None

        daemon = GEventWSGIDaemon(address=address,
                                  port=port,
                                  pidfile=pidfile,
                                  working_dir=path.abspath(instance_dir),
                                  uid=uid,
                                  stdout=logfile,
                                  stderr=logfile)

        if real_command == 'start':
            _start(daemon)
        elif real_command == 'stop':
            _stop(daemon)
        elif real_command == 'restart':
            _stop(daemon)
            _start(daemon)

#------------------------------------------------------------------------------
def _start(daemon):
    log('Starting...')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect( (daemon.address, daemon.port) )
        log('ERROR: Address "%s:%s" already in use.' % (daemon.address, daemon.port))
        sys.exit(1)
    except socket.error:
        pass
    finally:
        sock.close()

    daemon.start()
    try:
        # wait to let the child process create the PID file
        tries = 0
        while tries < 10:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect( (daemon.address, daemon.port) )
                with open(daemon.pidfile, 'r') as pf:
                    pid = pf.read()
                log('Server is listening on "%s:%s" (PID: %s)'
                                     % (daemon.address, daemon.port, pid.strip()))
                sys.exit(0)
            except socket.error:
                tries += 1
                time.sleep(0.5)
            finally:
                sock.close()
        raise socket.error()
    except (IOError, socket.error):
        log('ERROR: Failed to start instance.')

#------------------------------------------------------------------------------
def _stop(daemon):
    log('Shutting down...')
    daemon.stop()
    log('Stopped')

#------------------------------------------------------------------------------
class GEventWSGIDaemon(Daemon):

    def __init__(self, address, port, pidfile, working_dir, uid=None, gid=None,
                 stdin=None, stdout=None, stderr=None):
        Daemon.__init__(self, pidfile=pidfile, working_dir=working_dir, uid=uid,
                        gid=gid, stdin=stdin, stdout=stdout, stderr=stderr)
        self.address = address
        self.port = port

    def run(self):
        run_server(self.working_dir, self.address, self.port)


