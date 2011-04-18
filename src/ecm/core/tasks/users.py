# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from ecm.core import api
from ecm.lib import eveapi

__date__ = "2011 4 18"
__author__ = "diabeteman"

import logging

from django.db import transaction
from django.contrib.auth.models import User, Group

from ecm.data.common.models import RegistrationProfile, UserAPIKey
from ecm.data.roles.models import CharacterOwnership, Title, Member
from django.conf import settings

logger = logging.getLogger(__name__)


#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_all_character_associations():
    try:
        logger.info("Updating character associations with players...")
        for user in User.objects.filter(is_active=True):
            update_character_associations(user)
        logger.info("Character associations updated")
    except:
        logger.exception("update failed")
        raise

#------------------------------------------------------------------------------
def update_character_associations(user):
    # we delete all the previous ownerships
    CharacterOwnership.objects.filter(owner=user).delete()
    # get all the user's registered api credentials
    user_apis = UserAPIKey.objects.filter(owner=user)
    for user_api in user_apis:
        try:
            ids = [ char.characterID for char in api.get_account_characters(user_api) ]
            for member in Member.objects.filter(characterID__in=ids):
                try:
                    ownership = member.ownership
                except CharacterOwnership.DoesNotExist:
                    ownership = CharacterOwnership()
                    ownership.character = member
                ownership.owner = user
                ownership.save()
        except eveapi.Error:
            user_api.is_valid = False
            user_api.save()
    
#------------------------------------------------------------------------------
@transaction.commit_on_success
def cleanup_unregistered_users():
    try:
        logger.info("Deleting unregistered users...")
        count = 0
        for profile in RegistrationProfile.objects.all():
            if profile.activation_key_expired():
                user = profile.user
                count += 1
                if not user.is_active:
                    logger.debug("activation key has exprired for '%s', deleting user..." % user.username)
                    user.delete()
                else:
                    # user has activated his/her account. we delete the activation key
                    profile.delete()
        logger.info("%d unregistered users deleted")
    except:
        logger.exception("cleanup failed")
        raise

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_all_users_accesses():
    try:
        logger.info("Updating user accesses from their in-game roles...")
        for user in User.objects.filter(is_active=True):
            update_user_accesses(user)
        logger.info("User accesses updated")
    except:
        logger.exception("update failed")
        raise

#------------------------------------------------------------------------------
def update_user_accesses(user):
    owned = CharacterOwnership.objects.filter(owner=user)
    titles = Title.objects.none()
    director = False
    for char in owned:
        director = char.character.is_director() or director
        titles |= char.character.titles.all()
    ids = titles.distinct().values_list("titleID", flat=True)
    user.groups.clear()
    for id in ids:
        user.groups.add(Group.objects.get(id=id))
    if director:
        user.groups.add(Group.objects.get(id=settings.DIRECTOR_GROUP_ID))
