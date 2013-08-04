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

__date__ = "2010-02-09"
__author__ = "diabeteman"


import logging

from django.db import transaction
from django.utils import timezone

from ecm.utils import tools
from ecm.apps.common import api
from ecm.apps.corp.models import Corporation
from ecm.apps.hr.models.member import MemberSession
from ecm.apps.common.models import UpdateDate
from ecm.apps.eve.models import CelestialObject
from ecm.apps.hr.models import Member, MemberDiff

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update():
    """
    Retrieve all corp members, with all basic information about them.
    If some members have left or have arrived we also store the diff in the database.

    If there's an error, nothing is written in the database
    """
    LOG.info("fetching /corp/MemberTracking.xml.aspx...")
    # connect to eve API
    api_conn = api.connect()
    # retrieve /corp/MemberTracking.xml.aspx
    membersApi = api_conn.corp.MemberTracking(characterID=api.get_charID(), extended=1)
    api.check_version(membersApi._meta.version)

    currentTime = timezone.make_aware(membersApi._meta.currentTime, timezone.utc)
    cachedUntil = timezone.make_aware(membersApi._meta.cachedUntil, timezone.utc)
    LOG.debug("current time : %s", str(currentTime))
    LOG.debug("cached util : %s", str(cachedUntil))

    LOG.debug("parsing api response...")
    newMembers = {}
    oldMembers = {}
    notCorped  = {}
    oldAccessLvls = {}
    oldOwners = {}
    my_corp = Corporation.objects.mine()

    # we get the old member list from the database
    for m in Member.objects.all():
        if m.corp == my_corp:
            oldMembers[m] = m
        else:
            notCorped[m] = m
        oldAccessLvls[m.characterID] = m.accessLvl
        oldOwners[m.characterID] = m.owner

    for member in membersApi.members:
        m = parseOneMember(member, my_corp)
        session = MemberSession(character_id = m.characterID,
                                session_begin = m.lastLogin,
                                session_end = m.lastLogoff,
                                session_seconds = (member.logoffDateTime-member.logonDateTime).seconds)
        
        dbsession = MemberSession.objects.filter(character_id = m.characterID,
                                                 session_begin = m.lastLogin)
        if len(dbsession) == 0:
            session.save()
        newMembers[m] = m

    diffs, leaved = getDiffs(oldMembers, newMembers, currentTime)
    # "leaved" is the list of members that leaved (not a list of MemberDiff but real Character objects)
    # If we delete the old members each time, then all the diffs in roles/titles will not match
    # as the foreign keys will be gone from the members table...
    for L in leaved:
        L.corp = None
        newMembers[L] = L

    LOG.info("%d members parsed, %d changes since last scan", len(newMembers), len(diffs))

    for m in notCorped.values():
        try:
            # if the previously "not corped" members can now be found in the "new members"
            # we do nothing
            newMembers[m]
        except KeyError:
            # if the previously "not corped" members still cannot be found in the "new members"
            # we add them again to the members list
            newMembers[m] = m

    for m in newMembers.values():
        try:
            # we restore the old access levels from the database
            m.accessLvl = oldAccessLvls[m.characterID]
            m.owner = oldOwners[m.characterID]
        except KeyError:
            # 'm' is a brand new member, his/her access level didn't exist before
            # we leave it to the default value '0'
            continue
    
    for m in newMembers.values():
        # to be sure to store the nicknames change, etc.
        # even if there are no diff, we always overwrite the members
        m.save()

    if len(oldMembers) > 0 and len(diffs) > 0 :
        for d in diffs:
            d.save()
        # we store the update time of the table
        UpdateDate.mark_updated(model=MemberDiff, date=currentTime)

    # we store the update time of the table
    UpdateDate.mark_updated(model=Member, date=currentTime)



#------------------------------------------------------------------------------
def parseOneMember(member, my_corp):
    try:
        location = CelestialObject.objects.get(itemID = member.locationID).itemName
    except CelestialObject.DoesNotExist:
        location = str(member.locationID)
    try:
        mem = Member.objects.get(characterID=member.characterID)
        mem.corp = my_corp
        mem.nickname   = member.title
        mem.baseID     = member.baseID
        mem.corpDate   = timezone.make_aware(member.startDateTime, timezone.utc)
        mem.lastLogin  = timezone.make_aware(member.logonDateTime, timezone.utc)
        mem.lastLogoff = timezone.make_aware(member.logoffDateTime, timezone.utc)
        mem.location   = location
        mem.locationID = member.locationID
        mem.ship       = member.shipType
        return mem
    except Member.DoesNotExist:
        return Member(corp        = my_corp,
                      characterID = member.characterID,
                      name        = member.name,
                      nickname    = member.title,
                      baseID      = member.baseID,
                      corpDate    = timezone.make_aware(member.startDateTime, timezone.utc),
                      lastLogin   = timezone.make_aware(member.logonDateTime, timezone.utc),
                      lastLogoff  = timezone.make_aware(member.logoffDateTime, timezone.utc),
                      location    = location,
                      locationID  = member.locationID,
                      ship        = member.shipType)

#------------------------------------------------------------------------------
def getDiffs(oldMembers, newMembers, date):
    removed, added = tools.diff(old_items=oldMembers, new_items=newMembers)

    diffs  = []

    LOG.debug("RESIGNED MEMBERS:")
    if not removed : LOG.debug("(none)")
    for oldmember in removed:
        LOG.debug("- %s (%s)", oldmember.name, oldmember.nickname)
        diffs.append(MemberDiff(member_id   = oldmember.characterID,
                                name        = oldmember.name,
                                nickname    = oldmember.nickname,
                                new=False, date=date))
    LOG.debug("NEW MEMBERS:")
    if not added : LOG.debug("(none)")
    for newmember in added:
        LOG.debug("+ %s (%s)", newmember.name, newmember.nickname)
        diffs.append(MemberDiff(member_id   = newmember.characterID,
                                name        = newmember.name,
                                nickname    = newmember.nickname,
                                new=True, date=date))
    return diffs, removed

