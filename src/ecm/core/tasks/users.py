# Copyright (c) 2010-2011 Robin Jarry
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
from ecm.data.scheduler.models import ScheduledTask

__date__ = "2011 4 18"
__author__ = "diabeteman"

import logging

from django.db import transaction
from django.template.context import RequestContext
from django.http import HttpRequest
from django.contrib.auth.models import User, Group, AnonymousUser
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives

from ecm.core.eve import api
from ecm.lib import eveapi
from ecm.data.common.models import RegistrationProfile, UserAPIKey
from ecm.data.roles.models import Title, Member

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
    logger.debug("Updating character ownerships for '%s'..." % user.username)
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
        except eveapi.Error as e:
            if e.code in [202, 203, 204, 205, 210, 211, 212]:
                # authentication failure error codes. 
                # This happens if the apiKey does not match the userID 
                # or if the account is disabled
                logger.warning("%s (user: '%s' userID: %d)" % (str(e), user.username, user_api.userID))
                user_api.is_valid = False
                user_api.error = str(e)
                invalid_apis.append(user_api)
            else:
                # for all other errors, we abort the operation so that
                # character associations are not deleted by mistake and 
                # therefore, that users find themselves with no access :)
                raise
        user_api.save()
    if invalid_apis:
        # we notify the user by email
        ctx_dict = {'site': settings.ECM_BASE_URL,
                    'user_name': user.username,
                    'invalid_apis': invalid_apis}
        dummy_request = HttpRequest()
        dummy_request.user = AnonymousUser()
        subject = render_to_string('auth/invalid_api_email_subject.txt', ctx_dict, 
                                   RequestContext(dummy_request))
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        txt_content = render_to_string('auth/invalid_api_email.txt', ctx_dict,
                                       RequestContext(dummy_request))
        html_content = render_to_string('auth/invalid_api_email.html', ctx_dict,
                                        RequestContext(dummy_request))
        msg = EmailMultiAlternatives(subject, body=txt_content, to=[user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.warning("API credentials for '%s' are invalid. User notified by email." % user.username)
    # we delete all the previous ownerships
    Member.objects.filter(owner=user).update(owner=None)
    # and save the new ones
    for member, user in new_ownerships:
        member.owner = user
        member.save()
        
#------------------------------------------------------------------------------
@transaction.commit_on_success
def cleanup_unregistered_users():
    try:
        logger.info("Deleting activation keys...")
        count = 0
        for profile in RegistrationProfile.objects.all():
            if profile.activation_key_expired():
                user = profile.user
                count += 1
                if user.is_active:
                    # user has activated his/her account. we delete the activation key
                    profile.delete()
                else:
                    logger.info("activation key has exprired for '%s', deleting user..." % user.username)
                    user.delete() # this will delete the profile along with the user
        logger.info("%d activation keys deleted" % count)
    except:
        logger.exception("cleanup failed")
        raise

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_all_users_accesses():
    try:
        t = ScheduledTask.objects.get(function__contains='update_all_character_associations')
        if not t.is_last_exec_success:
            raise RuntimeWarning("Last character associations update failed. "
                                 "Skipping user access update.")
        logger.info("Updating user accesses from their in-game roles...")
        for user in User.objects.filter(is_active=True):
            update_user_accesses(user)
        logger.info("User accesses updated")
    except:
        logger.exception("update failed")
        raise

#------------------------------------------------------------------------------
def update_user_accesses(user):
    ownedCharacters = user.characters.all()
    titles = Title.objects.none()
    director = False
    for char in ownedCharacters:
        director = char.is_director() or director
        titles |= char.titles.all()
    ids = titles.distinct().values_list("titleID", flat=True)
    user.groups.clear()
    for id in ids:
        user.groups.add(Group.objects.get(id=id))
    if director:
        user.groups.add(Group.objects.get(id=settings.DIRECTOR_GROUP_ID))
