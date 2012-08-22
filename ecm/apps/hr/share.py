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
from ecm.apps.hr.models.member import Member

__date__ = "2012 08 01"
__author__ = "diabeteman"

from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone


@transaction.commit_on_success
def process_members(corp, data):
    corp.members.all().delete()
    
    for member in data:
        corp.members.create(**member)

@transaction.commit_on_success
def process_players(corp, data):
    User.objects.filter(is_active=False, username__endswith=corp.ticker).delete()
    
    for player in data:
        user, _ = User.objects.get_or_create(username='%s_%s' % (player['username'], corp.ticker), 
                                             is_active=False,
                                             password='', 
                                             first_name='',
                                             last_name='',
                                             email=str(corp.corporationID),
                                             last_login=timezone.now(),
                                             date_joined=timezone.now())
        
        Member.objects.filter(characterID__in=player['characters']).update(owner=user)
