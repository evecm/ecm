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

from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from django.shortcuts import render_to_response

from ecm.utils import json
from ecm.utils.usage_feedback.models import ECMInstanceFeedback

#------------------------------------------------------------------------------
STATS_PER_COUNTRY_SQL = '''\
SELECT  MAX(key_fingerprint) AS key_fingerprint,
        country_name,
        SUM(active_user_count) as active_users
FROM usage_feedback_ecminstancefeedback
GROUP BY country_name
ORDER BY active_users DESC;
'''

STATS_PER_CITY_SQL = '''\
SELECT  MAX(key_fingerprint) AS key_fingerprint,
        city,
        country_name,
        SUM(active_user_count) as active_users,
        COUNT(*) as instance_count
FROM usage_feedback_ecminstancefeedback
GROUP BY city, country_name;
'''

@csrf_exempt
def feedback(request):
    if request.method == 'POST':
        return post_feedback(request)
    else:
        return get_feedback(request)

@transaction.commit_on_success
def post_feedback(request):
    feedback = json.loads(request.body)
    key = feedback.get('key_fingerprint')


    try:
        db_feedback = ECMInstanceFeedback.objects.get(key_fingerprint=key)
        if db_feedback.last_updated > timezone.now() - timedelta(days=1):
            return HttpResponse('You cannot send feedback more than once a day')
    except ECMInstanceFeedback.DoesNotExist:
        db_feedback = ECMInstanceFeedback(key_fingerprint=feedback.get('key_fingerprint'),
                                          public_key=feedback.get('public_key'))

    db_feedback.url = feedback.get('url')
    db_feedback.corp_id = feedback.get('corp_id')
    db_feedback.corp_name = feedback.get('corp_name')
    db_feedback.eve_char_count = feedback.get('eve_char_count')
    db_feedback.active_user_count = feedback.get('active_user_count')
    db_feedback.avg_last_visit_top10 = feedback.get('avg_last_visit_top10')
    db_feedback.avg_last_visit = feedback.get('avg_last_visit')
    db_feedback.country_code = feedback.get('country_code')
    db_feedback.country_name = feedback.get('country_name')
    db_feedback.city = feedback.get('city')
    db_feedback.latitude = feedback.get('latitude')
    db_feedback.longitude = feedback.get('longitude')
    db_feedback.first_installed = feedback.get('first_installed')

    db_feedback.feedback_count += 1
    db_feedback.save()
    return HttpResponse('Thank you for your contribution')

def get_feedback(request):
    usage_per_country = ECMInstanceFeedback.objects.raw(STATS_PER_COUNTRY_SQL)
    top_instances = ECMInstanceFeedback.objects.order_by('-active_user_count')[:10]
    for instance in top_instances:
        instance.avg_last_visit = timedelta(seconds=instance.avg_last_visit or 0)
        instance.avg_last_visit_top10 = timedelta(seconds=instance.avg_last_visit_top10 or 0)

    try:
        last_update = ECMInstanceFeedback.objects.latest('last_updated').last_updated
    except ECMInstanceFeedback.DoesNotExist:
        last_update = 'None'

    data = {
        'last_update': last_update,
        'usage_per_country': usage_per_country,
        'top_countries': usage_per_country[:10],
        'usage_per_city': ECMInstanceFeedback.objects.raw(STATS_PER_CITY_SQL),
        'top_instances': top_instances,
    }
    return render_to_response('feedback.html', data)

