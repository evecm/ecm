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

__date__ = '2012 3 23'
__author__ = 'diabeteman'

import os
import sys

from ecm.admin.util import run_python_cmd, log

#-------------------------------------------------------------------------------
def collect_static_files(instance_dir, options):
    log("Gathering static files...")
    switches = '--noinput'
    if os.name != 'nt' and options.symlink_files:
        switches += ' --link'
    run_python_cmd('manage.py collectstatic ' + switches, instance_dir)

#------------------------------------------------------------------------------
def run_server(instance_dir, address, port, access_log=False):

    # workaround on osx, disable kqueue
    if sys.platform == "darwin":
        os.environ['EVENT_NOKQUEUE'] = "1"

    sys.path.insert(0, instance_dir)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    # This application object is used by any WSGI server configured to use this
    # file. This includes Django's development server, if the WSGI_APPLICATION
    # setting points here.
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()

    from gevent import monkey
    monkey.patch_all(dns=False)
    from gevent.pywsgi import WSGIServer

    if access_log:
        logfile = 'default'
    else:
        logfile = file(os.devnull, 'a+')

    server = WSGIServer((address, port), application, log=logfile)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.stop()

#------------------------------------------------------------------------------
