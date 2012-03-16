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
            api_chars = api.get_account_characters( user_api )
            chars = [ char.characterID for char in api_chars if char.is_corped ]
            conn = api.connect_user( user_api )
            for char in chars: #@ReservedAssignment
                member = Member.objects.get( characterID = char )
                sheet = conn.char.CharacterSheet( characterID = char )
                set_extended_char_attributes( member, sheet )
                set_character_skills( member, sheet)
        except eveapi.Error, err:
            if err.code == 0 or 200 <= err.code < 300:
                # authentication failure error codes.
                # This happens if the vCode does not match the keyID
                # or if the account is disabled
                # or if the key does not allow to list characters from an account
                LOG.warning("%s (user: '%s' keyID: %d)" % (str(err), user.username, user_api.keyID))
                user_api.is_valid = False
                user_api.error = str(err)
                user_api.save()
            else:
                # for all other errors, we abort the operation so that
                # character associations are not deleted by mistake and
                # therefore, that users find themselves with no access :)
                LOG.error("%d: %s (user: '%s' keyID: %d)" % (err.code, str(err), user.username, user_api.keyID))
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
    member.bloodLine = sheet.bloodLine
    member.ancestry = sheet.ancestry
    member.gender = sheet.gender
    member.corporationName = sheet.corporationName
    member.corporationID = sheet.corporationID
    try:
        member.allianceName = sheet.allianceName
        member.allianceID = sheet.allianceID
    except AttributeError:
        member.allianceName = None
        member.allianceID = 0
    member.cloneName = sheet.cloneName
    member.cloneSkillPoints = sheet.cloneSkillPoints
    member.balance = sheet.balance
    try:
        member.memoryBonusName = sheet.memoryBonusName
        member.memoryBonusValue = sheet.memoryBonusValue
    except AttributeError:
        member.memoryBonusName = None
        member.memoryBonusValue = 0
    try:
        member.intelligenceBonusName = sheet.intelligenceBonusName
        member.intelligenceBonusValue = sheet.intelligenceBonusValue
    except AttributeError:
        member.intelligenceBonusName = None
        member.intelligenceBonusValue = 0
    try:
        member.charismaBonusName = sheet.charismaBonusName
        member.charismaBonusValue = sheet.charismaBonusValue
    except AttributeError:
        member.charismaBonusName = None
        member.charismaBonusValue = 0
    try:
        member.willpowerBonusName = sheet.willpowerBonusName
        member.willpowerBonusValue = sheet.willpowerBonusValue
    except AttributeError:
        member.willpowerBonusName = None
        member.willpowerBonusValue = 0
    try:
        member.perceptionBonusName = sheet.perceptionBonusName
        member.perceptionBonusValue = sheet.perceptionBonusValue
    except AttributeError:
        member.perceptionBonusName = None
        member.perceptionBonusValue = 0
    member.intelligence = sheet.attributes.intelligence
    member.memory = sheet.attributes.memory
    member.charisma = sheet.attributes.charisma
    member.perception = sheet.attributes.perception
    member.willpower = sheet.attributes.willpower
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
    """
    This function will update django users' accesses (that is which groups they are in).
    
    It must be executed *AFTER* ecm.apps.hr.tasks.titles.update() which creates all Group 
    objects synchronized with in-game Titles. This function also adds 2 more Groups: 
    "Members" and "Directors" which are not in-game titles but can be usefull for handling 
    accesses to some parts of the application.
    
    After the execution, all django users will have been put into the Groups that match
    their owned characters' in-game titles.
    
    @see: ecm.apps.common.models.UrlPermission (django model)
    @see: ecm.views.decorators.check_user_access (decorator)
    """
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
def update_user_accesses(user, 
                         corp_members_group = Group.objects.get(name = 'Members'), 
                         directors_group = Group.objects.get(name = 'Directors')):
    """
    Synchronizes a user's groups with his/hers owned characters' in-game titles.
    """
    owned_characters = user.characters.all()
    titles = Title.objects.none() # we start with an empty QuerySet
    director = False
    for char in owned_characters:
        director = char.is_director or director
        titles |= char.titles.all() # the "|" operator concatenates django QuerySets
    all_titles = titles.distinct() # to remove duplicates if the same title is assigned to multiple characters
    user.groups.clear()
    if owned_characters.filter(corped=True):
        user.groups.add(corp_members_group)
    for titleID in all_titles.values_list("titleID", flat=True):
        user.groups.add(Group.objects.get(id=titleID))
    if director:
        user.groups.add(directors_group)
