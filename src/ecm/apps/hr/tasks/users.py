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
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives

from ecm.core.eve import api
from ecm.lib import eveapi
from ecm import settings
from ecm.apps.common.models import UserAPIKey
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

#------------------------------------------------------------------------------
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
        ctx_dict = {'site': settings.ECM_BASE_URL,
                    'user_name': user.username,
                    'invalid_apis': invalid_apis}
        dummy_request = HttpRequest()
        dummy_request.user = AnonymousUser()
        subject = render_to_string('email/invalid_api_subject.txt', ctx_dict,
                                   Ctx(dummy_request))
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        txt_content = render_to_string('email/invalid_api.txt', ctx_dict,
                                       Ctx(dummy_request))
        html_content = render_to_string('email/invalid_api.html', ctx_dict,
                                        Ctx(dummy_request))
        msg = EmailMultiAlternatives(subject, body=txt_content, to=[user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        LOG.warning("API credentials for '%s' are invalid. User notified by email." % user.username)
    # we delete all the previous ownerships
    Member.objects.filter(owner=user).update(owner=None)
    # and save the new ones
    for member, user in new_ownerships:
        member.owner = user
        member.save()

#------------------------------------------------------------------------------
try:
    DIRECTORS = Group.objects.get(name=settings.DIRECTOR_GROUP_NAME)
except Group.DoesNotExist:
    try:
        LOG.info('Group "%s" does not exists. Creating...' % settings.DIRECTOR_GROUP_NAME)
        DIRECTORS = Group.objects.create(name=settings.DIRECTOR_GROUP_NAME)
    except:
        LOG.exception("")
        raise
#------------------------------------------------------------------------------
try:
    MEMBERS = Group.objects.get(name=settings.CORP_MEMBERS_GROUP_NAME)
except Group.DoesNotExist:
    try:
        LOG.info('Group "%s" does not exists. Creating...' % settings.DIRECTOR_GROUP_NAME)
        MEMBERS = Group.objects.create(name=settings.CORP_MEMBERS_GROUP_NAME)
    except:
        LOG.exception("")
        raise
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
    LOG.info("Updating user accesses from their in-game roles...")
    for user in User.objects.filter(is_active=True):
        update_user_accesses(user)
    LOG.info("User accesses updated")

#------------------------------------------------------------------------------
def update_user_accesses(user):
    ownedCharacters = user.characters.all()
    titles = Title.objects.none()
    director = False
    for char in ownedCharacters:
        director = char.is_director or director
        titles |= char.titles.all()
    titleIDs = titles.distinct().values_list("titleID", flat=True)
    user.groups.clear()
    if ownedCharacters.filter(corped=True):
        user.groups.add(MEMBERS)
    for titleID in titleIDs:
        user.groups.add(Group.objects.get(id=titleID))
    if director:
        user.groups.add(DIRECTORS)
