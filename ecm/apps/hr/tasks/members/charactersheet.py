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

__date__ = '2012 3 16'
__author__ = 'diabeteman'

import logging

from django.contrib.auth.models import User
from django.db import transaction

from ecm.apps.common import api
from ecm.apps.common.auth import alert_user_for_invalid_apis
from ecm.apps.hr.models.member import Skill, Member
from ecm.apps.common.models import UserAPIKey
from ecm.lib import eveapi

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def update_extended_characters_info():
    LOG.debug("Updating character associations with players...")
    for user in User.objects.filter(is_active=True):
        update_one_user_extended_characters_info(user)
    LOG.info("Character associations updated")

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_one_user_extended_characters_info(user):
    invalid_apis = []
    for user_api in UserAPIKey.objects.filter(user=user):
        try:
            api_chars = api.get_account_characters(user_api)
            character_ids = [ char.characterID for char in api_chars ]
            conn = api.connect_user(user_api)
            for char_id in character_ids: #@ReservedAssignment
                try:
                    member = Member.objects.get(characterID=char_id)
                    sheet = conn.char.CharacterSheet(characterID=char_id)
                    set_extended_char_attributes(member, sheet)
                    set_character_skills(member, sheet)
                except Member.DoesNotExist:
                    # skip if character is not in the Members table yet
                    continue
        except eveapi.Error, err:
            if err.code == 0 or 200 <= err.code < 300:
                # authentication failure error codes.
                # This happens if the vCode does not match the keyID
                #   or if the account is disabled
                #   or if the key does not allow to list characters from an account
                LOG.warning("%s (user: '%s' keyID: %d)", str(err), user.username, user_api.keyID)
                user_api.is_valid = False
                user_api.error = str(err)
                invalid_apis.append(user_api)
            else:
                # for all other errors, we abort the operation so that
                # character associations are not deleted by mistake and
                # therefore, that users find themselves with no access :)
                LOG.error("%d: %s (user: '%s' keyID: %d)", err.code, str(err),
                                                           user.username, user_api.keyID)
                raise
        user_api.save()

    if invalid_apis:
        # we notify the user by email
        alert_user_for_invalid_apis(user, invalid_apis)

#-----------------------------------------------------------------------------
def set_character_skills(member, sheet):
    for skill in sheet.skills:
        sk, _ = Skill.objects.get_or_create(character=member, eve_type_id=skill.typeID)
        sk.skillpoints = skill.skillpoints
        sk.level = skill.level
        sk.save()

#-----------------------------------------------------------------------------
def set_extended_char_attributes(member, sheet):
    member.DoB = sheet.DoB
    member.race = sheet.race
    member.bloodLine = sheet.bloodLine
    member.ancestry = sheet.ancestry
    member.gender = sheet.gender
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
