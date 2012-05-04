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

from ecm.apps.eve import api
from ecm.lib import eveapi
from ecm.apps.common.auth import get_members_group, get_directors_group, alert_user_for_invalid_apis
from ecm.apps.hr.models import Title, Member
from ecm.apps.scheduler.models import ScheduledTask

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_all_character_associations():
    LOG.info("Updating character associations with players...")
    for user in User.objects.filter(is_active=True):
        update_character_associations(user)
    LOG.info("Character associations updated")

#-----------------------------------------------------------------------------
def update_character_associations(user):
    LOG.debug("Updating character ownerships for '%s'..." % user.username)
    invalid_apis = []
    new_ownerships = []
    # get all the user's registered api credentials
    for user_api in user.eve_accounts.all():
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
        alert_user_for_invalid_apis(user, invalid_apis)
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
        
    corp_members_group = get_members_group()
    directors_group = get_directors_group()
    
    LOG.info("Updating user accesses from their in-game roles...")
    for user in User.objects.filter(is_active=True):
        update_user_accesses(user, corp_members_group, directors_group)
    LOG.info("User accesses updated")

#------------------------------------------------------------------------------
def update_user_accesses(user, corp_members_group=None, directors_group=None):
    """
    Synchronizes a user's groups with his/hers owned characters' in-game titles.
    """
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
    if owned_characters.filter(corped=True):
        user.groups.add(corp_members_group)
    for titleID in all_titles.values_list("titleID", flat=True):
        user.groups.add(Group.objects.get(id=titleID))
    if director:
        user.groups.add(directors_group)

