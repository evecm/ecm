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

__date__ = '2012-07-18'
__author__ = 'Ajurna'

from django.contrib.auth.models import User

from ecm.apps.common import api
from ecm.apps.hr.models.member import Member

#------------------------------------------------------------------------------
def update():
    '''
    This is to pull all non corped characters accociated with accounts.
    These should be visible to the users involved.
    '''
    for user in User.objects.filter(is_active=True):
        for account in user.eve_accounts.all():
            if account.is_valid == True:
                for char in api.get_account_characters(account):
                    if not char.is_corped:
                        try:
                            mem = Member.objects.get(characterID = char.characterID)
                        except Member.DoesNotExist:
                            mem = add_char(user, char)
                        update_location(account, mem)

#------------------------------------------------------------------------------
def update_location(account, mem):
    conn = api.connect_user(account)
    ci = conn.eve.CharacterInfo(characterID = mem.characterID)
    mem.location = ci.lastKnownLocation
    mem.ship = ci.shipTypeName
    mem.owner = account.user
    mem.save()
    
#------------------------------------------------------------------------------
def add_char(user, char):
    mem = Member()
    mem.characterID = char.characterID
    mem.name = char.name
    mem.corped = False
    mem.owner = user
    return mem
    