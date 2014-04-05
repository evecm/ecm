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

__date__ = "2010-02-08"
__author__ = "diabeteman"


import logging
import urlparse
import urllib2

from django.db import models
from django.core.exceptions import ValidationError

from ecm.utils import _json as json
from ecm.apps.scheduler.validators import extract_function
from ecm.utils.http import HttpClient

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class Hangar(models.Model):
    
    DEFAULT_NAMES = {
        0: 'N/A',
        1: 'Deliveries',
        1000: 'Hangar division 1',
        1001: 'Hangar division 2',
        1002: 'Hangar division 3',
        1003: 'Hangar division 4',
        1004: 'Hangar division 5',
        1005: 'Hangar division 6',
        1006: 'Hangar division 7',
    }

    class Meta:
        ordering = ['hangarID']

    hangarID = models.PositiveIntegerField(primary_key=True)

    def get_name(self, corp):
        try:
            return self.corp_hangars.get(corp=corp, hangar=self).name
        except CorpHangar.DoesNotExist:
            return Hangar.DEFAULT_NAMES[self.hangarID]
        
    def get_access_lvl(self, corp):
        try:
            return self.corp_hangars.get(corp=corp, hangar=self).access_lvl
        except CorpHangar.DoesNotExist:
            return 1000

    def __unicode__(self):
        return unicode(self.hangarID)

#------------------------------------------------------------------------------
class CorpHangar(models.Model):

    class Meta:
        unique_together = ('corp', 'hangar')
        ordering = ('corp', 'hangar')

    corp = models.ForeignKey('Corporation', related_name='hangars')    
    hangar = models.ForeignKey('Hangar', related_name='corp_hangars')
    
    name = models.CharField(max_length=128)
    access_lvl = models.PositiveIntegerField(default=1000)
    
    def __unicode__(self):
        return unicode(self.name)

#------------------------------------------------------------------------------
class Wallet(models.Model):
    
    DEFAULT_NAMES = {
        1000: 'Wallet division 1',
        1001: 'Wallet division 2',
        1002: 'Wallet division 3',
        1003: 'Wallet division 4',
        1004: 'Wallet division 5',
        1005: 'Wallet division 6',
        1006: 'Wallet division 7',
        10000: 'Mercenary wallet division',
    }
    
    class Meta:
        ordering = ['walletID']

    walletID = models.PositiveIntegerField(primary_key=True)

    def get_name(self, corp):
        try:
            return self.corp_wallets.get(corp=corp, wallet=self).name
        except CorpWallet.DoesNotExist:
            return Wallet.DEFAULT_NAMES[self.walletID]

    def get_access_lvl(self, corp):
        try:
            return self.corp_wallets.get(corp=corp, wallet=self).access_lvl
        except CorpWallet.DoesNotExist:
            return 1000

    def __unicode__(self):
        return unicode(self.walletID)

#------------------------------------------------------------------------------
class CorpWallet(models.Model):
    
    class Meta:
        unique_together = ('corp', 'wallet')
        ordering = ('corp', 'wallet')
    
    corp = models.ForeignKey('Corporation', related_name='wallets')    
    wallet = models.ForeignKey('Wallet', related_name='corp_wallets')
    
    name = models.CharField(max_length=128)
    access_lvl = models.PositiveIntegerField(default=1000)
    
    def __unicode__(self):
        return unicode(self.name)

#------------------------------------------------------------------------------
class CorpManager(models.Manager):
    
    def mine(self):
        return self.get(is_my_corp=True) 
    
    def others(self):
        return self.filter(is_my_corp=False)

#------------------------------------------------------------------------------
class Alliance(models.Model):
    allianceID = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    shortName = models.CharField(max_length=10)
    def __unicode__(self):
        return unicode(self.name)

#------------------------------------------------------------------------------
class Corporation(models.Model):
    
    objects = CorpManager()
    
    ecm_url         = models.CharField(max_length=200, blank=True, null=True)
    is_my_corp      = models.BooleanField(default=False)
    is_trusted      = models.BooleanField(default=False)

    corporationID   = models.BigIntegerField(primary_key=True, blank=True)
    corporationName = models.CharField(max_length=256, blank=True, null=True)
    ticker          = models.CharField(max_length=8, blank=True, null=True)
    ceoID           = models.BigIntegerField(blank=True, null=True)
    ceoName         = models.CharField(max_length=256, blank=True, null=True)
    stationID       = models.BigIntegerField(blank=True, null=True)
    stationName     = models.CharField(max_length=256, blank=True, null=True)
    alliance        = models.ForeignKey(Alliance, related_name='corporations', blank=True, null=True)
    description     = models.TextField(blank=True, null=True)
    taxRate         = models.IntegerField(blank=True, null=True)
    memberLimit     = models.IntegerField(blank=True, null=True)

    private_key     = models.TextField(blank=True, null=True)
    public_key      = models.TextField(blank=True, null=True)
    key_fingerprint = models.CharField(max_length=255, blank=True, null=True)
    
    last_update     = models.DateTimeField(auto_now=True)
    
    #override
    def clean(self):
        if self.ecm_url and not (self.key_fingerprint and self.public_key):
            self.contact_corp(self.ecm_url)
    
    def save(self, force_insert=False, force_update=False, using=None):
        self.ecm_url = self.ecm_url or None
        self.private_key = self.private_key or None
        self.public_key = self.public_key or None
        self.key_fingerprint = self.key_fingerprint or None
        models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using)
    
    def contact_corp(self, corp_url):
        try:
            my_corp = Corporation.objects.mine()
            url = urlparse.urljoin(corp_url, '/corp/contact/')
        
            client = HttpClient()
            LOG.info('Sending our public info to %s...' % url)
            # first GET request to fetch CSRF cookie
            response = client.get(url)
            # second POST request to send our public info
            response = client.post(url, json.dumps(my_corp.get_public_info()))
            
            LOG.info('Fetching public info from %s...' % url)
            # the response should contain the corp's public info
            public_info = json.load(response)
            self.corporationID = public_info['corporationID']
            self.corporationName = public_info['corporationName']
            self.ticker = public_info['ticker']
            self.alliance_id = public_info['alliance']
            self.public_key = public_info['public_key']
            self.key_fingerprint = public_info['key_fingerprint']
            self.is_my_corp = False
            self.is_trusted = True
            
            LOG.info('Corp %s accepted our contact request.' % self.corporationName)
            LOG.info('Wait until they confirm that they trust us '
                     'before you can exchange data with them.')
        except urllib2.HTTPError, e:
            message = 'URL: %s, Response: %s %s "%s"' % (e.url, e.code, e.reason, e.read())
            LOG.exception(message)
            raise ValidationError(message)
        except Exception, e:
            LOG.exception('')
            raise ValidationError(e)
        
    def get_allowed_shares(self):
        shares = SharedData.objects.none()
        for group in self.corp_groups.all():
            shares |= group.allowed_shares.all()
        return shares.distinct()
    
    def get_public_info(self):
        public_info = {
            'ecm_url': self.ecm_url,
            'corporationID': self.corporationID,
            'corporationName': self.corporationName,
            'ticker': self.ticker,
            'alliance': self.alliance_id,
            'public_key': self.public_key,
            'key_fingerprint': self.key_fingerprint,
        }
        return public_info
    
    def get_corp_details(self):
        corp_details = {
            'corporationID': self.corporationID,
            'corporationName': self.corporationName,
            'ticker': self.ticker,
            'alliance': self.alliance_id,
            'ceoID': self.ceoID,
            'ceoName': self.ceoName,
            'stationID': self.stationID,
            'stationName': self.stationName,
            'description': self.description,
            'taxRate': self.taxRate,
            'memberLimit': self.memberLimit,
        }
        return corp_details
    
    def set_corp_details(self, details):
        self.corporationName = details['corporationName']
        self.ticker = details['ticker']
        self.alliance_id = details['alliance']
        self.ceoID = details['ceoID']
        self.ceoName = details['ceoName']
        self.stationID = details['stationID']
        self.stationName = details['stationName']
        self.description = details['description']
        self.taxRate = details['taxRate']
        self.memberLimit = details['memberLimit']
        
    
    def __unicode__(self):
        return unicode(self.corporationName)
    
    def __eq__(self, other):
        return isinstance(other, Corporation) and self.corporationID == other.corporationID
    
    def __hash__(self):
        return self.corporationID

#------------------------------------------------------------------------------
class Standing(models.Model):
    
    class Meta:
        ordering = ('-value', 'contactName',)
    
    corp = models.ForeignKey('Corporation', related_name='standings')
    contactID = models.BigIntegerField(default=0)
    contactName = models.CharField(max_length=255)
    is_corp_contact = models.BooleanField(default=True)
    value = models.IntegerField(default=0)
    
    @property
    def contact_type(self):
        #https://forums.eveonline.com/default.aspx?g=posts&m=716708#post716708
        #Characters: ]90000000, 98000000[
        #Corporations: ]98000000, 99000000[
        #Alliances: ]99000000, 100000000[
        #Note: This is not accurate and should not be used until a better solution is found.
        if self.contactID > 90000000 and self.contactID < 98000000:
            return 'Character'
        elif self.contactID > 98000000 and self.contactID < 99000000:
            return 'Corporation'
        elif self.contactID > 99000000 and self.contactID < 100000000:
            return 'Alliance'
        else:
            return unicode(self.contactID)
    
    def __unicode__(self):
        return unicode(self.contactName)

    
#------------------------------------------------------------------------------
class CorpGroup(models.Model):
    
    name = models.CharField(primary_key=True, max_length=100)
    corporations = models.ManyToManyField('Corporation', related_name='corp_groups')
    allowed_shares = models.ManyToManyField('SharedData', related_name='shared_datas') 

    def __unicode__(self):
        return self.name
    
#------------------------------------------------------------------------------
class SharedData(models.Model):
    
    url = models.CharField(primary_key=True, max_length=255, editable=False)
    handler = models.CharField(max_length=255, editable=False)
    
    def call_handler(self, *args, **kwargs):
        function = extract_function(self.handler)
        return function(*args, **kwargs)
    
    def __unicode__(self):
        return self.url
