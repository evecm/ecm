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

__date__ = "2012 08 02"
__author__ = "Ajurna"

from django.db.models.aggregates import Count
from django.template.context import RequestContext as Ctx
from django.shortcuts import render_to_response
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed

from ecm.utils import _json as json
from ecm.apps.common import eft
from ecm.apps.eve.models import Type
from ecm.views.decorators import check_user_access
from ecm.views import JSON
from ecm.apps.common.models import ColorThreshold, UpdateDate
from ecm.apps.hr.models import Member
from ecm.views import DATATABLES_DEFAULTS
from ecm.apps.hr.views import get_members, MEMBERS_COLUMNS
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.apps.corp.models import Corporation


#------------------------------------------------------------------------------
@check_user_access()
def skills_search(request):
    
    corps = Corporation.objects.others().order_by('corporationName')
    corps = corps.annotate(member_count=Count('members'))
    
    data = {
        'scan_date' : UpdateDate.get_latest(Member),
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL,
        'datatables_defaults': DATATABLES_DEFAULTS,
        'columns': MEMBERS_COLUMNS,
        'ajax_url': '/hr/members/skills/data/',
        'trusted_corps': corps.filter(member_count__gt=0, is_trusted=True),
        'other_corps': corps.filter(member_count__gt=0, is_trusted=False),
    }
    
    return render_to_response('ecm/hr/members/skills.html', data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def skilled_list(request):
    try:
        params = extract_datatable_params(request)
        corp_id = request.GET.get('corp')
        skills = json.loads(request.GET.get("skills", ""))
    except KeyError:
        return HttpResponseBadRequest()

    if corp_id:
        try:
            members = Corporation.objects.get(corporationID=int(corp_id)).members.all()
        except Corporation.DoesNotExist:
            members = Corporation.objects.mine().members.all()
        except ValueError:
            # corp_id cannot be casted to int, we take all corps
            members = Member.objects.exclude(corp=None)
    else:
        members = Corporation.objects.mine().members.all()

    query = members
    for skill in skills:
        query &= members.filter(skills__eve_type_id=skill['id'], 
                                skills__level__gte=skill['lvl'])
    
    total_members,\
    filtered_members,\
    members = get_members(query=query.distinct(),
                          first_id=params.first_id,
                          last_id=params.last_id,
                          sort_by=params.column,
                          asc=params.asc)
    
    return datatable_ajax_data(members, params.sEcho, total_members, filtered_members)

#------------------------------------------------------------------------------
@check_user_access()
def extract_filter_items(request):
    items = []
    valid_item = True
    for key, value in request.POST.items(): #@UnusedVariable
        try:
            typeID = int(key)
            item = Type.objects.get(typeID=typeID, category__in = [6, 7, 16])
            items.append((item,))
        except ValueError:
            pass
        except Type.DoesNotExist:
            valid_item = False
    return items, valid_item

#------------------------------------------------------------------------------
@check_user_access()
def parse_eft(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed()

    eft_block = request.POST.get('eft_block', None)
    if not eft_block:
        return HttpResponseBadRequest('Empty EFT block')

    eft_items = eft.parse_export(eft_block)

    query = Type.objects.filter(typeName__in=eft_items.keys())
    items = {}
    for item in query:
        for sk in item.skill_reqs.all():
            try:
                if items[sk.skill] < sk.required_level:
                    items[sk.skill] = sk.required_level
            except KeyError:
                items[sk.skill] = sk.required_level
    out = []
    for item in items:
        out.append({
            'typeID': item.typeID,
            'typeName': item.typeName,
            'level': items[item],
        })
    return HttpResponse(json.dumps(out), mimetype=JSON)

#------------------------------------------------------------------------------
@check_user_access()
def get_item_id(request):
    querystring = request.GET.get('q', None)
    if querystring is not None:
        query = Type.objects.filter(typeName__iexact=querystring).filter(category__in = [6, 7, 16])
        if query.exists():
            item = query[0]
            out = []
            if item.categoryID == 16:
                out.append([item.typeID, item.typeName, 1])
            for i in item.skill_reqs.all():
                out.append([i.skill.typeID, i.skill.typeName, i.required_level])
            return HttpResponse(json.dumps(out), mimetype=JSON)
        else:
            return HttpResponseNotFound('Item <em>%s</em> not Skill, Ship or Module.' % querystring)
    else:
        return HttpResponseBadRequest('Missing "q" parameter.')

#------------------------------------------------------------------------------
@check_user_access()
def search_item(request):
    querystring = request.GET.get('q', None)
    try:
        limit = int(request.GET.get('limit', "10"))
    except ValueError:
        limit = 10
    if querystring is not None:
        query = Type.objects.filter(typeName__icontains=querystring, category__in = [6, 7, 16]).order_by('typeName')
        matches = query[:limit].values_list('typeName', flat=True)
        return HttpResponse('\n'.join(matches))
    else:
        return HttpResponseBadRequest('Missing "q" parameter.')