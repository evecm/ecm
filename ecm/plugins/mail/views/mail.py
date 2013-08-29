# Copyright (c) 2010-2011 Jerome Vacher
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

__date__ = "2012 09 06"
__author__ = "Ajurna"

from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext as tr
from django.contrib.contenttypes.models import ContentType

from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params, datatable_ajax_data, datatable_csv_data
from ecm.plugins.mail.models import Mail, Recipient, MailingList
from ecm.apps.hr.models.member import Member
from ecm.apps.corp.models import Corporation, Alliance
from ecm.views import DATATABLES_DEFAULTS
from ecm.utils.format import print_time_min

COLUMNS = [
    {'sTitle': tr('Sent Date'),    'sWidth': '10%',   'db_field': 'sentDate', },
    {'sTitle': tr('Sender'),       'sWidth': '15%',   'db_field': 'sender', },
    {'sTitle': tr('Recipients'),   'sWidth': '25%',   'bSortable': False},
    {'sTitle': tr('Title'),        'sWidth': '50%',   'db_field': 'title', },
    {'sTitle': tr('id'),           'bVisible': False, 'db_field': 'id', },
]

#------------------------------------------------------------------------------
@check_user_access()
def mail_list(request):
    corps = set()
    alliances = set()
    corp_type = ContentType.objects.get(app_label="corp", model="corporation")
    alliance_type = ContentType.objects.get(app_label="corp", model="alliance")
    for corp in Recipient.objects.filter(content_type=corp_type):
        corps.add(corp.recipient)
    for ally in Recipient.objects.filter(content_type=alliance_type):
        alliances.add(ally.recipient)
    data = {
        'corps'               : corps,
        'alliances'           : alliances,
        'maillists'           : MailingList.objects.all(),
        'datatables_defaults' : DATATABLES_DEFAULTS,
        'columns'             : COLUMNS,
        'sorting'             : [[0, 'desc']],
        'ajax_url'            : '/mail/data/',
    }
    return render_to_response("ecm/mail/mail_list.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
def mail_message(request, msg_id):
    mail = Mail.objects.get(messageID=msg_id)
    recipients = mail.recipients.all()
    data = {
            'message'    : mail,
            'recipients' : recipients,
        }
    
    return render_to_response("ecm/mail/mail_message.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
def mail_list_data(request):
    
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
    except:
        return HttpResponseBadRequest()
    total_count = Mail.objects.all().count()

    recfilter = False
    #These are mutually exclusive
    if REQ.get('ally') != '0':
        recipients = Recipient.objects.filter(object_id=REQ.get('ally'))
        recfilter = True
    elif REQ.get('corp') != '0':
        recipients = Recipient.objects.filter(object_id=REQ.get('corp'))
        recfilter = True
    elif REQ.get('maillist') != '0':
        recipients = Recipient.objects.filter(object_id=REQ.get('maillist'))
        recfilter = True
    elif REQ.get('to'):
        recipients = []
        mem = Member.objects.filter(name__contains=REQ.get('to'))
        recipients += Recipient.objects.filter(object_id__in=mem)
        cor = Corporation.objects.filter(corporationName__contains=REQ.get('to'))
        recipients += Recipient.objects.filter(object_id__in=cor)
        all = Alliance.objects.filter(name__contains=REQ.get('to'))
        recipients += Recipient.objects.filter(object_id__in=all)
        recfilter = True
    else:
        recipients = []

    if recfilter == True:
        mail = Mail.objects.filter(recipients__in=recipients).distinct().order_by(COLUMNS[params.column]['db_field'])
    else:
        mail = Mail.objects.all().order_by(COLUMNS[params.column]['db_field'])

    if REQ.get('from'):
        mail = mail.filter(sender__name__contains=REQ.get('from'))

    if not params.asc:
        mail = mail.reverse()

    mail_list = []
    if params.format == 'csv':
        for message in mail[params.first_id:params.last_id]:
            recp = []
            for target in message.recipients.all():
                recp.append(str(target))
            if len(recp) > 1:
                recipients = ', '.join(recp)
            else:
                recipients = recp[0]
            mail_list.append([print_time_min(message.sentDate),
                              message.sender.name,
                              recipients,
                              message.title,
                              message.body])
        return datatable_csv_data(mail_list, filename='mails.csv')
    else:
        for message in mail[params.first_id:params.last_id]:
            recp = []
            for target in message.recipients.all():
                recp.append(str(target))
            if len(recp) > 1:
                recipients = ', '.join(recp)
            else:
                recipients = recp[0]
            mail_list.append([print_time_min(message.sentDate),
                              message.sender.name,
                              recipients,
                              message.modal_link,
                              message.messageID])
        return datatable_ajax_data(mail_list, params.sEcho, total_count, len(mail))