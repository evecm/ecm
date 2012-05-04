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

__date__ = '2012-05-06'
__author__ = 'diabeteman'

import multiprocessing

#------------------------------------------------------------------------------
def _async_callback(*tasks):
    """
    This function is a callback for multiprocessing.Process#target
    
    All the tasks passed as arguments must run in a separate process,
    therefore, the db connection must be reset in order to avoid bugs with
    Postgresql and other delicate db servers. 
    """
    from django import db
    # we loose the reference to the old connection, this process cannot use it
    db.connection.connection = None
    # force create a new db connection
    db.connection.cursor()
    
    for task in tasks:
        task.run()

#------------------------------------------------------------------------------
def run_async(*tasks):
    proc = multiprocessing.Process(target=_async_callback, args=tasks)
    proc.start()
