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

from django.conf import settings
from django.contrib.auth.models import Group, AnonymousUser
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from django.template.context import RequestContext as Ctx

from ecm.apps.common.models import Setting

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def get_directors_group():
    return get_or_create_group(Setting.get('hr_directors_group_name'))

#------------------------------------------------------------------------------
def get_recruiters_group():
    return get_or_create_group(Setting.get('hr_recruiters_group_name'))

#------------------------------------------------------------------------------
def get_members_group():
    return get_or_create_group(Setting.get('hr_corp_members_group_name'))

#------------------------------------------------------------------------------
def get_allies_plus_5_group():
    return get_or_create_group(Setting.get('hr_allies_plus_5_group_name'))

#------------------------------------------------------------------------------
def get_allies_plus_10_group():
    return get_or_create_group(Setting.get('hr_allies_plus_10_group_name'))

#------------------------------------------------------------------------------
def get_or_create_group(group_name):
    try:
        return Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        LOG.info('Group "%s" does not exists. Creating...' % group_name)
        return Group.objects.create(name=group_name)

#------------------------------------------------------------------------------
def alert_user_for_invalid_apis(user, invalid_apis):
    from ecm.views import HTML
    ctx_dict = {
        'host_name': settings.EXTERNAL_HOST_NAME,
        'use_https': settings.USE_HTTPS,
        'user_name':user.username,
        'invalid_apis':invalid_apis
    }
    dummy_request = HttpRequest()
    dummy_request.user = AnonymousUser()

    subject = render_to_string('ecm/common/email/invalid_api_subject.txt', ctx_dict, Ctx(dummy_request))
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    txt_content = render_to_string('ecm/common/email/invalid_api.txt', ctx_dict, Ctx(dummy_request))
    html_content = render_to_string('ecm/common/email/invalid_api.html', ctx_dict, Ctx(dummy_request))

    msg = EmailMultiAlternatives(subject, body=txt_content, to=[user.email])
    msg.attach_alternative(html_content, mimetype=HTML)
    msg.send()

    LOG.warning("API credentials for '%s' are invalid. User notified by email." % user.username)
