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

from django.db import transaction
from django.utils import timezone

from ecm.plugins.mail.models import Mail, MailingList, Notification, Recipient
from ecm.apps.common import api
from ecm.apps.common.models import UserAPIKey
from ecm.apps.hr.models.member import Member

#-----------------------------------------------------------------------------
def update():
    for key in UserAPIKey.objects.filter(is_valid = True):
        api_conn = api.connect_user(key)
        #TODO: put api check here!
        for char in api_conn.account.Characters().characters:
            get_mailing_lists(api_conn, char.characterID)
            get_mail(api_conn, char.characterID)
            get_notifications(api_conn, char.characterID)

#-----------------------------------------------------------------------------
@transaction.commit_on_success
def get_notifications(api_conn, charid):
    headers = api_conn.char.Notifications(characterID=charid)
    mem = Member.objects.get(characterID=charid)
    headerlist = []
    for head in headers.notifications:
        try:
            Notification.objects.get(notificationID = head.notificationID)
        except Notification.DoesNotExist:
            headerlist.append(head.notificationID)
            note = Notification()
            note.notificationID = head.notificationID
            note.recipient = mem
            note.senderID = head.senderID
            note.typeID = head.typeID
            note.sentDate = timezone.make_aware(head.sentDate, timezone.utc)
            note.save()
    if not headerlist == []:
        bodies = api_conn.char.NotificationTexts(characterID = charid, ids = headerlist)
        for body in bodies.notifications:
            try:
                note = Notification.objects.get(notificationID = body.notificationID)
                note.body = body.data
                note.save()
            except Mail.DoesNotExist:
                pass

#-----------------------------------------------------------------------------
def pull_corp_or_alliance(idn):
    if id > 98000000 and id < 99000000:
        return api.pull_corporation(idn)
    else:
        return api.pull_alliance(idn)

#-----------------------------------------------------------------------------
@transaction.commit_on_success
def get_mail(api_conn, charid):
    headers = api_conn.char.MailMessages(characterID=charid)
    headerlist = []
    for head in headers.messages:
        try:
            Mail.objects.get(messageID=head.messageID)
        except Mail.DoesNotExist:
            headerlist.append(head.messageID)
            mail = Mail()
            mail.messageID = head.messageID
            try:
                mem = Member.objects.get(characterID = head.senderID)
            except Member.DoesNotExist:
                mem = api.pull_character(head.senderID)
            mail.sender = mem    
            mail.sentDate = timezone.make_aware(head.sentDate, timezone.utc)
            mail.title = head.title
            mail.save()
            if not head.toCorpOrAllianceID == '':
                rec = Recipient()
                rec.mail = mail
                rec.recipient = pull_corp_or_alliance(head.toCorpOrAllianceID)
                rec.save()
            for chid in str(head.toCharacterIDs).split(','):
                if chid == '':
                    break
                try:
                    mem = Member.objects.get(characterID = chid)
                except Member.DoesNotExist:
                    mem = api.pull_character(chid)
                rec = Recipient()
                rec.mail = mail
                rec.recipient = mem
                rec.save()
            if not head.toListID == '':
                try:
                    lis = MailingList.objects.get(listID=head.toListID)
                except MailingList.DoesNotExist:
                    lis = head.toListID
                rec = Recipient()
                rec.mail = mail
                rec.recipient = lis
                rec.save()
    #Get Message Body
    if not headerlist == []:
        bodies = api_conn.char.MailBodies(characterID = charid, ids = headerlist)
        for body in bodies.messages:
            try:
                msg = Mail.objects.get(messageID = body.messageID)
                msg.body = body.data
                msg.save()
            except Mail.DoesNotExist:
                pass

#-----------------------------------------------------------------------------
@transaction.commit_on_success
def get_mailing_lists(api_conn, charid):
    lists = api_conn.char.mailinglists(characterID=charid)
    for li in lists.mailingLists:
        try:
            MailingList.objects.get(listID=li.listID)
        except MailingList.DoesNotExist:
            ml = MailingList()
            ml.listID = li.listID
            ml.displayName = li.displayName
            ml.save()
