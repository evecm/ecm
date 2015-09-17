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

__date__ = "2010-02-11"
__author__ = "diabeteman"

import logging

from django.db import transaction
from django.utils import timezone

from ecm.utils import tools
from ecm.apps.common.models import UpdateDate
from ecm.apps.common import api
from ecm.apps.corp.models import Corporation
from ecm.apps.hr.models.titles import Title
from ecm.apps.hr.models import RoleMembership, TitleMembership, RoleMemberDiff, \
    TitleMemberDiff, Member, RoleType, Role

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update():
    """
    Retrieve all corp members' titles and roles.
    We store all the changes in the database

    If there's an error, nothing is written in the database
    """
    LOG.info("fetching /corp/MemberSecurity.xml.aspx...")
    # connect to eve API
    api_conn = api.connect()
    # retrieve /corp/MemberTracking.xml.aspx
    memberSecuApi = api_conn.corp.MemberSecurity(characterID=api.get_charID())
    api.check_version(memberSecuApi._meta.version)

    currentTime = timezone.make_aware(memberSecuApi._meta.currentTime, timezone.utc)
    cachedUntil = timezone.make_aware(memberSecuApi._meta.cachedUntil, timezone.utc)
    LOG.debug("current time : %s", str(currentTime))
    LOG.debug("cached util : %s", str(cachedUntil))

    LOG.debug("parsing api response...")
    oldRoles  = {}
    oldTitles = {}

    # we fetch the old data from the database
    for role in RoleMembership.objects.all():
        oldRoles[role] = role
    for title in TitleMembership.objects.all():
        oldTitles[title] = title

    newRoles  = {}
    newTitles = {}

    # for performance, we fetch all the Roles & RoleTypes here
    allRoleTypes = RoleType.objects.all()
    allRoles = {}
    for role in Role.objects.all():
        allRoles[(role.roleID, role.roleType_id)] = role
        
    my_corp = Corporation.objects.mine()
    
    all_members = Member.objects.all()
    
    for member in memberSecuApi.members:
        if all_members.filter(characterID=member.characterID):
            # only get roles/titles for existing members.
            newRoles.update(parseOneMemberRoles(member, allRoleTypes, allRoles))
            newTitles.update(parseOneMemberTitles(member, my_corp))

    # Store role changes
    roleDiffs = storeRoles(oldRoles, newRoles, currentTime)

    # Store title changes
    titleDiffs = storeTitles(oldTitles, newTitles, currentTime)
    LOG.info("%d role changes, %d title changes", roleDiffs, titleDiffs)

    # update members access levels
    for m in Member.objects.all():
        m.accessLvl = m.get_access_lvl()
        m.save()


#------------------------------------------------------------------------------
def parseOneMemberRoles(member, allRoleTypes, allRoles):
    roles = {}

    for roleCategory in allRoleTypes:
        # we analyse each role category for this member
        for role in member[roleCategory.typeName] :
            # each role has a sub id within its category
            roleSubID = role.roleID
            # we have to resolve the global role id from the category id and the role sub id.
            globalRoleID = allRoles[(roleSubID, roleCategory.id)].id
            # then we can create a new membership item for the current member and this role
            membership = RoleMembership(member_id=member.characterID, role_id=globalRoleID)
            roles[membership] = membership

    return roles

#------------------------------------------------------------------------------
def parseOneMemberTitles(member, my_corp):
    titles = {}
 
    if 'titles' in member:
        for t in member.titles:
            try:
                title = Title.objects.get(corp=my_corp, titleID=t.titleID)
                membership = TitleMembership(member_id=member.characterID, title=title)
                titles[membership] = membership
            except:
                # It's possible that a member has a title that doesn't exist in the database, because the API doesn't return default titles
                # Just consider it a non title since there are no roles anyway.
                pass
 
    return titles

#------------------------------------------------------------------------------
def __storeRoleDiffs(removed, added, date):
    diffs    = []
    LOG.debug("REMOVED ROLES:")
    if not removed :
        LOG.debug("(none)")
    for remrole in removed:
        LOG.debug("- " + unicode(remrole))
        diffs.append(RoleMemberDiff(role_id   = remrole.role_id,
                                    member_id = remrole.member_id,
                                    new=False, date=date))
    LOG.debug("ADDED ROLES:")
    if not added :
        LOG.debug("(none)")
    for addrole in added:
        LOG.debug("+ " + unicode(addrole))
        diffs.append(RoleMemberDiff(role_id   = addrole.role_id,
                                    member_id = addrole.member_id,
                                    new=True, date=date))

    return diffs

def getRoleMemberDiffs(oldRoles, newRoles, date):
    removed, added = tools.diff(new_items=newRoles, old_items=oldRoles)
    return __storeRoleDiffs(removed, added, date)
#------------------------------------------------------------------------------
def __storeTitleDiffs(removed, added, date):
    diffs = []
    LOG.debug("REMOVED TITLES:")
    if not removed:
        LOG.debug("(none)")
    for remtitle in removed:
        LOG.debug("- " + unicode(remtitle))
        diffs.append(TitleMemberDiff(title_id=remtitle.title_id,
                                     member_id=remtitle.member_id,
                                     new=False, date=date))

    LOG.debug("ADDED TITLES:")
    if not added:
        LOG.debug("(none)")
    for addtitle in added:
        LOG.debug("+ " + unicode(addtitle))
        diffs.append(TitleMemberDiff(title_id=addtitle.title_id,
                                     member_id=addtitle.member_id,
                                     new=True, date=date))

    return diffs

def getTitleMemberDiffs(oldTitles, newTitles, date):
    removed, added = tools.diff(new_items=newTitles, old_items=oldTitles)
    return __storeTitleDiffs(removed, added, date)
#------------------------------------------------------------------------------
def storeRoles(oldRoles, newRoles, date):
    if len(oldRoles) != 0:
        roleDiffs = getRoleMemberDiffs(oldRoles, newRoles, date)
        if roleDiffs:
            for d in roleDiffs: d.save()
            # we store the update time of the table
            UpdateDate.mark_updated(model=RoleMemberDiff, date=date)

            RoleMembership.objects.all().delete()
            for rm in newRoles.values(): rm.save()
            # we store the update time of the table
            UpdateDate.mark_updated(model=RoleMembership, date=date)
        # if no diff, we do nothing
        return len(roleDiffs)
    else:
        # 1st import, no diff to write
        for rm in newRoles.values(): rm.save()
        # we store the update time of the table
        UpdateDate.mark_updated(model=RoleMembership, date=date)
        return 0

#------------------------------------------------------------------------------
def storeTitles(oldTitles, newTitles, date):
    if len(oldTitles) != 0:
        titleDiffs = getTitleMemberDiffs(oldTitles, newTitles, date)
        if titleDiffs:
            for d in titleDiffs:
                try:
                    d.save()
                except Database.Warning:
                    # When DEBUG=true, MySQLdb warnings get counted as exceptions, and there's often a "Warning: Field 'id' doesn't have a default value"
                    # thrown here.  Ignore it.  https://github.com/evecm/ecm/issues/14
                    pass
            # we store the update time of the table
            UpdateDate.mark_updated(model=TitleMemberDiff, date=date)

            TitleMembership.objects.all().delete()
            for tm in newTitles.values(): tm.save()
            # we store the update time of the table
            UpdateDate.mark_updated(model=TitleMembership, date=date)
        # if no diff, we do nothing
        return len(titleDiffs)
    else:
        # 1st import, no diff to write
        for tm in newTitles.values(): tm.save()
        # we store the update time of the table
        UpdateDate.mark_updated(model=TitleMembership, date=date)
        return 0

