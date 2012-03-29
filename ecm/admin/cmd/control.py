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

import sys
import time
from os import path
from ConfigParser import SafeConfigParser
from optparse import OptionParser

from ecm.lib.subcommand import Subcommand
from ecm.admin.util import get_logger
from ecm.lib.daemon import Daemon

#------------------------------------------------------------------------------
def sub_command():
    cmd = Subcommand('start', aliases=('stop', 'restart', 'status'),
                     parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                     help='Control the embedded server of an existing ECM instance.',
                     callback=run)
    return cmd

#------------------------------------------------------------------------------
def run(command, global_options, options, args):
    if not args:
        command.parser.error('Missing instance directory.')
    instance_dir = args[0]

    log = get_logger()

    config = SafeConfigParser()
    settings_file = path.join(instance_dir, 'settings.ini')
    if not config.read([settings_file]):
        command.parser.error('Settings file "%s" not found.' % settings_file)

    pidfile = config.get('misc', 'pid_file') or 'ecm.pid'
    address = config.get('misc', 'server_bind_ip') or '127.0.0.1'
    port = config.get('misc', 'server_bind_port') or 8888
    run_as_user = config.get('misc', 'run_as_user') or None

    if not path.isabs(pidfile):
        pidfile = path.abspath(path.join(instance_dir, pidfile))

    real_command = sys.argv[1]

    if real_command == 'status':
        if path.isfile(pidfile):
            with open(pidfile, 'r') as pf:
                pid = pf.read()
            log.info('Instance is running with PID: %s' % pid.strip())
        else:
            log.info('Instance is stopped')
        sys.exit(0)
    else:
        if run_as_user:
            import pwd
            uid = pwd.getpwnam(run_as_user)
        else:
            uid = None
        
        daemon = GEventWSGIDaemon(address=address, 
                                  port=port, 
                                  pidfile=pidfile, 
                                  working_dir=path.abspath(instance_dir), 
                                  uid=uid)
        if real_command == 'start':
            _start(daemon, pidfile, log)
        elif real_command == 'stop':
            _stop(daemon, log)
        elif real_command == 'restart':
            _stop(daemon, log)
            _start(daemon, pidfile, log)

#------------------------------------------------------------------------------
def _start(daemon, pidfile, log):
    log.info('Instance starting...')
    daemon.start()
    try:
        with open(pidfile, 'r') as pf:
            pid = pf.read()
        log.info('Instance is running with PID: %s' % pid.strip())
    except IOError:
        log.info('Start instance failed')

#------------------------------------------------------------------------------
def _stop(daemon, log):
    log.info('Instance is shutting down...')
    daemon.stop()
    log.info('Instance is stopped')

#------------------------------------------------------------------------------
class GEventWSGIDaemon(Daemon):

    def __init__(self, address, port, pidfile, working_dir, uid=None, gid=None, 
                 stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        Daemon.__init__(self, pidfile=pidfile, working_dir=working_dir, uid=uid, 
                        gid=gid, stdin=stdin, stdout=stdout, stderr=stderr)
        self.address = address 
        self.port = port

    def run(self):
        self._setup_environ()
        try:
            from gevent.pywsgi import WSGIServer
        except ImportError:
            print >>sys.stderr, 'Please install "gevent" to run this command.'
            sys.exit(1)
        import django.core.handlers.wsgi
        application = django.core.handlers.wsgi.WSGIHandler()
        server = WSGIServer((self.address, self.port), application)
        server.serve_forever()

    def _setup_environ(self):
        sys.path.insert(0, self.working_dir)
        
        import settings #@UnresolvedImport

        from django.core import management

        management.setup_environ(settings)
        utility = management.ManagementUtility()
        command = utility.fetch_command('runserver')
        command.validate()

        from django.conf import settings as django_settings
        from django.utils import translation
        translation.activate(django_settings.LANGUAGE_CODE)
