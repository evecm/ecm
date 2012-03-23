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

__date__ = "2012-02-18"
__author__ = "diabeteman"

# This is a gunicorn config for ECM
import os
def numCPUs():
    if not hasattr(os, "sysconf"):
        raise RuntimeError("No sysconf detected.")
    return os.sysconf("SC_NPROCESSORS_ONLN")
bind = '127.0.0.1:8080'
workers = numCPUs() + 1
worker_class = 'egg:gunicorn#gevent'
user = 'www-data'
preload_app = True
accesslog = '/var/log/gunicorn/ecm_access.log'
errorlog = '/var/log/gunicorn/ecm_error.log'
proc_name = 'gunicorn_ecm'

