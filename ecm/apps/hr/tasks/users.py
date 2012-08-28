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
from django.contrib.auth.models import User, Group

from ecm.lib import eveapi
from ecm.apps.common import api
from ecm.apps.corp.models import Corporation
from ecm.apps.common.auth import get_members_group, get_directors_group, alert_user_for_invalid_apis
from ecm.apps.hr.models import Title, Member
from ecm.apps.hr.tasks.charactersheet import set_extended_char_attributes, get_character_skills
from ecm.apps.scheduler.models import ScheduledTask

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def update_all_character_associations():
    LOG.info("Updating character associations with players...")
    for user in User.objects.filter(is_active=True):
        update_character_associations(user)
    LOG.info("Character associations updated")

#-----------------------------------------------------------------------------
def update_character_associations(user):
    LOG.debug("Updating character ownerships for '%s'..." % user.username)
    eve_accounts = []
    invalid_api_keys = []
    new_characters = []
    new_corps = set()
    skills = []
    
    # get all the user's registered api credentials
    for api_key in user.eve_accounts.all():
        try:
            conn = api.connect_user(api_key)
            for char in api.get_account_characters(api_key):
                try:
                    member = Member.objects.get(characterID=char.characterID)
                except Member.DoesNotExist:
                    member = Member(characterID=char.characterID,
                                    name=char.name)
                
                corp = __get_corp(char)
                if member.corp != corp:
                    member.corp = corp
                    new_corps.add(corp)
                
                if char.is_corped:
                    sheet = conn.char.CharacterSheet(characterID=member.characterID)
                    set_extended_char_attributes(member, sheet)
                    skills.extend(get_character_skills(member, sheet))
                
                new_characters.append(member)
            api_key.is_valid = True
        except eveapi.Error, e:
            if e.code == 0 or 200 <= e.code < 300:
                # authentication failure error codes.
                # This happens if the vCode does not match the keyID
                # or if the account is disabled
                # or if the key does not allow to list characters from an account
                LOG.warning("%s (user: '%s' keyID: %d)" % (str(e), user.username, api_key.keyID))
                api_key.is_valid = False
                api_key.error = str(e)
                invalid_api_keys.append(api_key)
            else:
                # for all other errors, we abort the operation so that
                # character associations are not deleted by mistake and
                # therefore, that users find themselves with no access :)
                LOG.error("%d: %s (user: '%s' keyID: %d)" % (e.code, str(e), user.username, api_key.keyID))
                raise
        eve_accounts.append(api_key)
    
    if invalid_api_keys:
        # we notify the user by email
        alert_user_for_invalid_apis(user, invalid_api_keys)
    
    # this goes in a separate function to shorten DB transactions
    save_all(user, new_characters, eve_accounts, new_corps, skills)
    
#-----------------------------------------------------------------------------
@transaction.commit_on_success
def save_all(user, characters, eve_accounts, new_corps, skills):
    for account in eve_accounts:
        account.save()
    for corp in new_corps:
        corp.save()
    # we delete all the previous ownerships
    Member.objects.filter(owner=user).update(owner=None)
    # and save the new ones
    for char in characters:
        char.owner = user
        char.save()
    for skill in skills:
        skill.save()

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
        
    corp_members_group = get_members_group()
    directors_group = get_directors_group()
    my_corp = Corporation.objects.mine()
    
    LOG.info("Updating user accesses from their in-game roles...")
    for user in User.objects.filter(is_active=True):
        update_user_accesses(user, my_corp, corp_members_group, directors_group)
    LOG.info("User accesses updated")

#------------------------------------------------------------------------------
def update_user_accesses(user, my_corp=None, corp_members_group=None, directors_group=None):
    """
    Synchronizes a user's groups with his/hers owned characters' in-game titles.
    """
    my_corp = my_corp or Corporation.objects.mine()
    corp_members_group = corp_members_group or get_members_group()
    directors_group = directors_group or get_directors_group()
    owned_characters = user.characters.all()
    titles = Title.objects.none() # we start with an empty QuerySet
    director = False
    for char in owned_characters:
        director = char.is_director or director
        titles |= char.titles.all() # the "|" operator concatenates django QuerySets
    all_titles = titles.distinct() # to remove duplicates if the same title is assigned to multiple characters
    user.groups.clear()
    if owned_characters.filter(corp=my_corp):
        user.groups.add(corp_members_group)
    for titleID in all_titles.values_list("titleID", flat=True):
        user.groups.add(Group.objects.get(id=titleID))
    if director:
        user.groups.add(directors_group)

#------------------------------------------------------------------------------
def __get_corp(char):
    try:
        return Corporation.objects.get(corporationID=char.corporationID)
    except Corporation.DoesNotExist:
        conn = eveapi.EVEAPIConnection(scheme='http')
        api_corp = conn.corp.CorporationSheet(corporationID=char.corporationID)
        return Corporation(corporationID=api_corp.corporationID,
                           corporationName=api_corp.corporationName,
                           ticker=api_corp.ticker,
                           )