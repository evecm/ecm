# Copyright (c) 2010-2013 Robin Jarry
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

__date__ = "2013 07 17"
__author__ = "diabeteman"

import logging
from pkg_resources import parse_version

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.template.context import RequestContext as Ctx
from django.template.loader import render_to_string
from django.core.mail import mail_admins
from django.utils.translation import ugettext_lazy as tr_lazy

import ecm
from ecm.apps.corp.models import Corporation
from ecm.apps.hr.models.member import MemberDiff
from ecm.apps.hr.models.titles import TitleMemberDiff, TitleCompoDiff
from ecm.apps.hr.models.roles import RoleMemberDiff
from ecm.apps.common.auth import get_members_group
from ecm.utils.usage_feedback import ECM_USAGE_FEEDBACK_URL
from ecm.utils.http import HttpClient
from ecm.utils import _json as json

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def send_feedback():
    """
    This function will collect basic non-critical data about the current server
    instance and send it to eve-corp-management.org official server for usage
    statistics feedback.
    """
    LOG.debug('Sending usage feedback to %r...', ECM_USAGE_FEEDBACK_URL)

    mycorp = Corporation.objects.mine()

    # fetch geolocalization info
    http_client = HttpClient()
    resp = http_client.get(url='http://freegeoip.net/json/')
    geoloc_info = json.loads(resp.read())
    resp.close()

    # we only consider users that are corp members
    users = get_members_group().user_set.order_by('-last_login')

    usage_data = {
        'key_fingerprint':      mycorp.key_fingerprint,

        'active_user_count':    users.count(),
        'avg_last_visit_top10': avg_last_login(users[:10]),
        'avg_last_visit':       avg_last_login(users),
        'first_installed':      find_oldest_entry(),

        'country_code':         geoloc_info.get('country_code'),
        'country_name':         geoloc_info.get('country_name'),
        'city':                 geoloc_info.get('city'),

        'ecm_version':          ecm.VERSION,
    }

    # send the data to the server
    resp = http_client.post(ECM_USAGE_FEEDBACK_URL, json.dumps(usage_data))
    LOG.info('Usage feedback sent to %r. Thank you for your contribution.',
             ECM_USAGE_FEEDBACK_URL)

    new_version = resp.read().strip()
    old_version = ecm.VERSION

    if parse_version(new_version) > parse_version(old_version):
        LOG.info('New version of ecm is available: %r.', new_version)

        ctx_dict = {
            'host_name': settings.EXTERNAL_HOST_NAME,
            'use_https': settings.USE_HTTPS,
            'new_version': new_version,
            'old_version': old_version,
        }

        dummy_request = HttpRequest()
        dummy_request.user = AnonymousUser()

        subject = tr_lazy('ECM version %s is available' % new_version)
        msg = render_to_string('ecm/common/email/new_version.txt',
                               ctx_dict, Ctx(dummy_request))
        html = render_to_string('ecm/common/email/new_version.html',
                                ctx_dict, Ctx(dummy_request))

        mail_admins(subject=subject, message=msg, html_message=html)


#------------------------------------------------------------------------------
def find_oldest_entry():
    try:
        oldest_memberdiff = MemberDiff.objects.order_by('date')[0].date
    except:
        oldest_memberdiff = timezone.now()
    try:
        oldest_titlememberdiff = TitleMemberDiff.objects.order_by('date')[0].date
    except:
        oldest_titlememberdiff = timezone.now()
    try:
        oldest_rolememberdiff = RoleMemberDiff.objects.order_by('date')[0].date
    except:
        oldest_rolememberdiff = timezone.now()
    try:
        oldest_titlecompodiff = TitleCompoDiff.objects.order_by('date')[0].date
    except:
        oldest_titlecompodiff = timezone.now()

    return min(oldest_memberdiff,
               oldest_titlememberdiff,
               oldest_rolememberdiff,
               oldest_titlecompodiff)

#------------------------------------------------------------------------------
SECONDS_PER_DAY = 60 * 60 * 24
def avg_last_login(users):
    now = timezone.now()

    # convert to a list of dates
    last_logins = users.values_list('last_login', flat=True)

    def __date_delta(date):
        delta = now - date
        return delta.days * SECONDS_PER_DAY + delta.seconds

    # convert to a list of timedelta compared to "now"
    last_logins = map(__date_delta, last_logins)

    if last_logins:
        # calculate the average last_login in seconds
        return int(reduce(lambda x, y: x + y, last_logins) / len(last_logins))
    else:
        return 0

