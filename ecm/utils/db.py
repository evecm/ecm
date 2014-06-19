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

__date__ = '2012 4 5'
__author__ = 'diabeteman'

from django.conf import settings

#------------------------------------------------------------------------------
def fix_mysql_quotes(query):
    """
    MySQL doesn't like double quotes. We replace them by backticks.
    """
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        return query.replace('"', '`')
    else:
        return query
        
def order_by_case_insensitive(query, sort_col, asc):
    """
    Sort a query by a field, but case insensitive
    """
    sort_col_lower = '%s_lower' % sort_col
    query = query.extra(select={sort_col_lower : 'lower(%s)' % sort_col})
    if not asc: sort_col_lower = '-' + sort_col_lower
    return query.order_by(sort_col_lower)
