# Copyright (c) 2010-2012 Robin Jarry
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software:     you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation:     either version 3 of the License:     or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful:    
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not:     see <http:    //www.gnu.org/licenses/>.

__date__ = "2012 04 10"
__author__ = "tash"

COLOR_FORMAT = '<font class="%s">%s</font>'

ORDER_STATES = {
0 :    'open / active',
1 :    'closed',
2 :    'expired (or fulfilled)',
3 :    'cancelled',
4 :    'pending',
5 :    'character deleted',
}

FORMATED_ORDER_STATES = {
0 :    COLOR_FORMAT % ('contract-inprogress', ORDER_STATES[0]),
1 :    COLOR_FORMAT % ('contract-completed', ORDER_STATES[1]),
2 :    COLOR_FORMAT % ('contract-completed', ORDER_STATES[2]),
3 :    COLOR_FORMAT % ('contract-cancelled', ORDER_STATES[3]),
4 :    COLOR_FORMAT % ('contract-inprogress', ORDER_STATES[4]),
5 :    COLOR_FORMAT % ('contract-deleted', ORDER_STATES[5]),
}

FORMATED_CONTRACT_STATES = {
'Outstanding':             COLOR_FORMAT % ('contract-outstanding', 'Outstanding'),
'Deleted':                 COLOR_FORMAT % ('contract-deleted', 'Deleted'),
'Completed':               COLOR_FORMAT % ('contract-completed', 'Completed'),
'Failed':                  COLOR_FORMAT % ('contract-failed', 'Failed'),
'CompletedByIssuer':       COLOR_FORMAT % ('contract-completedbyissuer', 'CompletedByIssuer'),
'CompletedByContractor':   COLOR_FORMAT % ('contract-completedbycontractor', 'CompletedByContractor'),
'Cancelled':               COLOR_FORMAT % ('contract-cancelled', 'Cancelled'),
'Rejected':                COLOR_FORMAT % ('contract-rejected', 'Rejected'),
'Reversed':                COLOR_FORMAT % ('contract-reversed', 'Reversed'),
'InProgress':              COLOR_FORMAT % ('contract-inprogress', 'InProgress'),
}











