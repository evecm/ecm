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

__date__ = "2011 4 18"
__author__ = "diabeteman"

import logging

from django.db import transaction
from django.template.context import RequestContext as Ctx
from django.http import HttpRequest
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives

from ecm.core import HTML
from ecm.apps.eve import api
from ecm.lib import eveapi
from ecm.apps.common.models import UserAPIKey, Setting
from ecm.apps.hr.models import Title, Member, Skill
from ecm.apps.scheduler.models import ScheduledTask

LOG = logging.getLogger(__name__)


#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_all_character_associations():
    LOG.info("Updating character associations with players...")
    for user in User.objects.filter(is_active=True):
        update_character_associations(user)
        if user.is_active:
            update_character_sheet(user)
    LOG.info("Character associations updated")

#------------------------------------------------------------------------------
def update_character_sheet(user):
    user_apis = UserAPIKey.objects.filter(user=user)
    for user_api in user_apis:
        try:
            ids = [ char.characterID for char in api.get_account_characters( user_api ) if char.is_corped ]
            conn = eveapi.EVEAPIConnection()
            api = conn.auth( keyID=user_api.keyID, vCode=user_api.vCode )
            for id in ids:
                member = Member.objects.filter( characterID = id )
                sheet = api.char.CharacterSheet( characterID = id )
                set_extended_char_attributes( member, sheet )
                set_character_skills( member, sheet)
        except eveapi.Error, e:
            if e.code == 0 or 200 <= e.code < 300:
                # authentication failure error codes.
                # This happens if the vCode does not match the keyID
                # or if the account is disabled
                # or if the key does not allow to list characters from an account
                LOG.warning("%s (user: '%s' keyID: %d)" % (str(e), user.username, user_api.keyID))
                user_api.is_valid = False
                user_api.error = str(e)
                #invalid_apis.append(user_api)
                user_api.save()
            else:
                # for all other errors, we abort the operation so that
                # character associations are not deleted by mistake and
                # therefore, that users find themselves with no access :)
                LOG.error("%d: %s (user: '%s' keyID: %d)" % (e.code, str(e), user.username, user_api.keyID))
                raise

#-----------------------------------------------------------------------------
def set_character_skills( member, sheet):
    for skill in sheet.skills:
        try:
            sk = Skill.objects.get(character=member, typeID=skill.typeID)
            sk.skillpoints = skill.skillpoints
            sk.level = skill.level
            sk.save()
        except Skill.DoesNotExist:
            sk = Skill(character=member,
                       typeID=skill.typeID,
                       skillpoints=skill.skillpoints,
                       level = skill.level)
            sk.save()

#-----------------------------------------------------------------------------
def set_extended_char_attributes(member, sheet):
    member.DoB = sheet.DoB
    member.race = sheet.race
    member.bloodLine = sheet.bloodline
    member.ancestry = sheet.ancestry
    member.gender = sheet.gender
    member.corporationName = sheet.corporationName
    member.corporationID = sheet.corporationID
    member.allianceName = sheet.allianceName
    member.allianceID = sheet.allianceID
    member.cloneName = sheet.cloneName
    member.CloneSkillPoints = sheet.CloneSkillPoints
    member.balance = sheet.balance
    member.memoryBonusName = sheet.memoryBonusName
    member.memoryBonusValue = sheet.memoryBonusValue
    member.intelligenceBonusName = sheet.intelligenceBonusName
    member.intelligenceBonusValue = sheet.intelligenceBonusValue
    member.charismaBonusName = sheet.charismaBonusName
    member.charismaBonusValue = sheet.charismaBonusValue
    member.willpowerBonusName = sheet.willpowerBonusName
    member.willpowerBonusValue = sheet.willpowerBonusValue
    member.perceptionBonusName = sheet.perceptionBonusName
    member.perceptionBonusValue = sheet.perceptionBonusValue
    member.intelligence = sheet.intelligence
    member.memory = sheet.memory
    member.charisma = sheet.charisma
    member.perception = sheet.perception
    member.willpower = sheet.willpower
    member.save()

#-----------------------------------------------------------------------------
def update_character_associations(user):
    LOG.debug("Updating character ownerships for '%s'..." % user.username)
    # get all the user's registered api credentials
    user_apis = UserAPIKey.objects.filter(user=user)
    invalid_apis = []
    new_ownerships = []
    for user_api in user_apis:
        try:
            ids = [ char.characterID for char in api.get_account_characters(user_api) if char.is_corped ]
            user_api.is_valid = True
            for member in Member.objects.filter(characterID__in=ids):
                new_ownerships.append((member, user))
        except eveapi.Error, e:
            if e.code == 0 or 200 <= e.code < 300:
                # authentication failure error codes.
                # This happens if the vCode does not match the keyID
                # or if the account is disabled
                # or if the key does not allow to list characters from an account
                LOG.warning("%s (user: '%s' keyID: %d)" % (str(e), user.username, user_api.keyID))
                user_api.is_valid = False
                user_api.error = str(e)
                invalid_apis.append(user_api)
            else:
                # for all other errors, we abort the operation so that
                # character associations are not deleted by mistake and
                # therefore, that users find themselves with no access :)
                LOG.error("%d: %s (user: '%s' keyID: %d)" % (e.code, str(e), user.username, user_api.keyID))
                raise
        user_api.save()
    if invalid_apis:
        # we notify the user by email
        ctx_dict = {'site': Site.objects.get_current(),
                    'user_name': user.username,
                    'invalid_apis': invalid_apis}
        dummy_request = HttpRequest()
        dummy_request.user = AnonymousUser()
        subject = render_to_string('email/invalid_api_subject.txt', ctx_dict, Ctx(dummy_request))
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        txt_content = render_to_string('email/invalid_api.txt', ctx_dict, Ctx(dummy_request))
        html_content = render_to_string('email/invalid_api.html', ctx_dict, Ctx(dummy_request))
        msg = EmailMultiAlternatives(subject, body=txt_content, to=[user.email])
        msg.attach_alternative(html_content, mimetype=HTML)
        msg.send()
        LOG.warning("API credentials for '%s' are invalid. User notified by email." % user.username)
    # we delete all the previous ownerships
    Member.objects.filter(owner=user).update(owner=None)
    # and save the new ones
    for member, user in new_ownerships:
        member.owner = user
        member.save()

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_all_users_accesses():
    try:
        t = ScheduledTask.objects.get(function__contains='update_all_character_associations')
        if not t.is_last_exec_success:
            raise RuntimeWarning("Last character associations update failed. "
                                 "Skipping user access update.")
    except ScheduledTask.DoesNotExist:
        pass
    
    directors_group_name = Setting.get('hr_directors_group_name')
    try:
        directors_group = Group.objects.get(name=directors_group_name)
    except Group.DoesNotExist:
        try:
            LOG.info('Group "%s" does not exists. Creating...' % directors_group_name)
            directors_group = Group.objects.create(name=directors_group_name)
        except:
            LOG.exception("")
            raise
    corp_members_group_name = Setting.get('hr_corp_members_group_name')
    try:
        corp_members_group = Group.objects.get(name=corp_members_group_name)
    except Group.DoesNotExist:
        try:
            LOG.info('Group "%s" does not exists. Creating...' % corp_members_group_name)
            corp_members_group = Group.objects.create(name=corp_members_group_name)
        except:
            LOG.exception("")
            raise
    
    LOG.info("Updating user accesses from their in-game roles...")
    for user in User.objects.filter(is_active=True):
        update_user_accesses(user, corp_members_group, directors_group)
    LOG.info("User accesses updated")

#------------------------------------------------------------------------------
def update_user_accesses(user, corp_members_group, directors_group):
    ownedCharacters = user.characters.all()
    titles = Title.objects.none()
    director = False
    for char in ownedCharacters:
        director = char.is_director or director
        titles |= char.titles.all()
    titleIDs = titles.distinct().values_list("titleID", flat=True)
    user.groups.clear()
    if ownedCharacters.filter(corped=True):
        user.groups.add(corp_members_group)
    for titleID in titleIDs:
        user.groups.add(Group.objects.get(id=titleID))
    if director:
        user.groups.add(directors_group)
