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
from ecm.utils.usage_feedback import ECM_USAGE_FEEDBACK_URL


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
def print_usage_feedback_message():
    log('')
    log('*ATTENTION*')
    log('')
    log('ECM now has usage feedback system which is enabled by default.')
    log('This feature is really helpfull for ECM developers because it allows')
    log('us to know how much the project is used and helps our motivation ;-)')
    log('')
    log('It consists in a scheduled task that will run once each week and send')
    log('*basic* and *anonymous* data to the official server %r.', ECM_USAGE_FEEDBACK_URL)
    log('This is *NOT* a spying system nor a backdoor to enter your ECM instance.')
    log('To know what data is sent in detail, please see the source code at http://eve-corp-management.org/projects/ecm/repository/entry/ecm/apps/common/tasks/usage_feedback.py')
    log('')
    log('If however you *really* want to disable the usage feedback on your')
    log('instance, you need to go to the admin panel and change the scheduled')
    log('task "ecm....send_feedback" to inactive.')
    log('')
    log('Thank you for using ECM. Fly safe.')
