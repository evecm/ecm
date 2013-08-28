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
# EVE Corporation Management. If not, see <>.

__date__ = "2012 09 06"
__author__ = "Ajurna"

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from ecm.apps.hr.models.member import Member

class Mail(models.Model):
    class Meta:
        verbose_name = "Mail"
        verbose_name_plural = "Mails"
    messageID = models.BigIntegerField(primary_key=True)
    sender = models.ForeignKey(Member, related_name='sent_mail')
    sentDate = models.DateTimeField()
    title = models.CharField(max_length=255, default="")
    body = models.TextField(default="")
    @property
    def url(self):
        return 'message/%d/' % self.messageID
    @property
    def permalink(self):
        return '<a href="%s" class="pos">%s</a>' % (self.url, self.title)
    @property
    def modal_link(self):
        return '<a href="%s" data-toggle="modal">%s</a>' % (self.url, self.title)
    def __unicode__(self):
        return unicode(self.title)

class MailingList(models.Model):
    class Meta:
        verbose_name = "Mailing List"
        verbose_name_plural = "Mailing Lists"
    listID = models.BigIntegerField(primary_key=True)
    displayName = models.CharField(max_length=255, default="")

class Recipient(models.Model):
    class Meta:
        verbose_name = 'Recipient'
        verbose_name_plural = 'Recipients'
    mail = models.ForeignKey(Mail, related_name='recipients')
    content_type = models.ForeignKey(ContentType)
    object_id = models.BigIntegerField()
    recipient = generic.GenericForeignKey('content_type', 'object_id')
    def __unicode__(self):
        return unicode(self.recipient)

class Notification(models.Model):
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
    TYPE = {
        1: 'Legacy',
        2: 'Character deleted',
        3: 'Give medal to character',
        4: 'Alliance maintenance bill',
        5: 'Alliance war declared',
        6: 'Alliance war surrender',
        7: 'Alliance war retracted',
        8: 'Alliance war invalidated by Concord',
        9: 'Bill issued to a character',
        10: 'Bill issued to corporation or alliance',
        11: "Bill not paid because there's not enough ISK available",
        12: 'Bill, issued by a character, paid',
        13: 'Bill, issued by a corporation or alliance, paid',
        14: 'Bounty claimed',
        15: 'Clone activated',
        16: 'New corp member application',
        17: 'Corp application rejected',
        18: 'Corp application accepted',
        19: 'Corp tax rate changed',
        20: 'Corp news report, typically for shareholders',
        21: 'Player leaves corp',
        22: 'Corp news, new CEO',
        23: 'Corp dividend/liquidation, sent to shareholders',
        24: 'Corp dividend payout, sent to shareholders',
        25: 'Corp vote created',
        26: 'Corp CEO votes revoked during voting',
        27: 'Corp declares war',
        28: 'Corp war has started',
        29: 'Corp surrenders war',
        30: 'Corp retracts war',
        31: 'Corp war invalidated by Concord',
        32: 'Container password retrieval',
        33: 'Contraband or low standings cause an attack or items being confiscated',
        34: 'First ship insurance',
        35: 'Ship destroyed, insurance payed',
        36: 'Insurance contract invalidated/runs out',
        37: 'Sovereignty claim fails (alliance)',
        38: 'Sovereignty claim fails (corporation)',
        39: 'Sovereignty bill late (alliance)',
        40: 'Sovereignty bill late (corporation)',
        41: 'Sovereignty claim lost (alliance)',
        42: 'Sovereignty claim lost (corporation)',
        43: 'Sovereignty claim acquired (alliance)',
        44: 'Sovereignty claim acquired (corporation)',
        45: 'Alliance anchoring alert',
        46: 'Alliance structure turns vulnerable',
        47: 'Alliance structure turns invulnerable',
        48: 'Sovereignty disruptor anchored',
        49: 'Structure won/lost',
        50: 'Corp office lease expiration notice',
        51: 'Clone contract revoked by station manager',
        52: 'Corp member clones moved between stations',
        53: 'Clone contract revoked by station manager',
        54: 'Insurance contract expired',
        55: 'Insurance contract issued',
        56: 'Jump clone destroyed',
        57: 'Jump clone destroyed',
        58: 'Corporation joining factional warfare',
        59: 'Corporation leaving factional warfare',
        60: 'Corporation kicked from factional warfare on startup because of too low standing to the faction',
        61: 'Character kicked from factional warfare on startup because of too low standing to the faction',
        62: 'Corporation in factional warfare warned on startup because of too low standing to the faction',
        63: 'Character in factional warfare warned on startup because of too low standing to the faction',
        64: 'Character loses factional warfare rank',
        65: 'Character gains factional warfare rank',
        66: 'Agent has moved',
        67: 'Mass transaction reversal message',
        68: 'Reimbursement message',
        69: 'Agent locates a character',
        70: 'Research mission becomes available from an agent',
        71: 'Agent mission offer expires',
        72: 'Agent mission times out',
        73: 'Agent offers a storyline mission',
        74: 'Tutorial message sent on character creation',
        75: 'Tower alert',
        76: 'Tower resource alert',
        77: 'Station aggression message',
        78: 'Station state change message',
        79: 'Station conquered message',
        80: 'Station aggression message',
        81: 'Corporation requests joining factional warfare',
        82: 'Corporation requests leaving factional warfare',
        83: 'Corporation withdrawing a request to join factional warfare',
        84: 'Corporation withdrawing a request to leave factional warfare',
        85: 'Corporation liquidation',
        86: 'Territorial Claim Unit under attack',
        87: 'Sovereignty Blockade Unit under attack',
        88: 'Infrastructure Hub under attack',
        89: 'Contact add notification',
        90: 'Contact edit notification',
        91: 'Incursion Completed',
        92: 'Corp Kicked',
        93: 'Customs office has been attacked',
        94: 'Customs office has entered reinforced',
        95: 'Customs office has been transferred',
        96: 'FW Alliance Warning',
        97: 'FW Alliance Kick',
        98: 'AllWarCorpJoined Msg',
        99: 'Ally Joined Defender',
        100: 'Ally Has Joined a War Aggressor',
        101: 'Ally Joined War Ally',
        102: 'New war system: entity is offering assistance in a war.',
        103: 'War Surrender Offer',
        104: 'War Surrender Declined',
        105: 'FacWar LP Payout Kill',
        106: 'FacWar LP Payout Event',
        107: 'FacWar LP Disqualified Eventd',
        108: 'FacWar LP Disqualified Kill,',
    }
    notificationID = models.BigIntegerField(primary_key=True)
    senderID = models.BigIntegerField()
    recipient = models.ForeignKey(Member, related_name='notifications')
    typeID = models.IntegerField(choices=TYPE.items())
    sentDate = models.DateTimeField()
    body = models.TextField()

