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

__date__ = '2012 3 24'
__author__ = 'diabeteman'

import os
import sys

from ecm.admin.util import run_command, get_logger

#-------------------------------------------------------------------------------
def collect_static_files(options):
    log = get_logger()
    log.info("Gathering static files...")
    run_dir = os.path.join(options.install_dir, 'ecm')
    run_command(sys.executable + ' manage.py collectstatic --noinput', run_dir)
