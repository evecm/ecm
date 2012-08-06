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

__date__ = '2012 08 01'
__author__ = 'diabeteman'

import logging
import urllib2
import urlparse

from ecm.utils.http import HttpClient
from ecm.utils import crypto
from ecm.apps.corp.models import Corporation

LOG = logging.getLogger(__name__)

def update_all():
    
    for corp in Corporation.objects.others():
        LOG.debug('Updating info from corp: %s' % corp.ecm_url)
        try:
            update_one_corp(corp)
        except urllib2.HTTPError, e:
            msg = e.fp.read()
            LOG.error(msg)
        
        
def update_one_corp(corp):
    
    my_corp = Corporation.objects.mine()
    
    auth_url = urlparse.urljoin(corp.ecm_url, '/corp/login/')
    client = HttpClient()
    
    response = client.get(auth_url, headers={'Authorization': 'RSA %s' % my_corp.key_fingerprint})
    cipher_txt_in = response.read()
    
    # we decrypt the response with our private key
    session_secret = crypto.rsa_decrypt(my_corp.private_key, cipher_txt_in)
    # and encrypt it back with the corp's public key
    cipher_txt_out = crypto.rsa_encrypt(corp.public_key, session_secret)
    
    # then send it to the server
    response = client.post(auth_url, cipher_txt_out)
    
    
    
    
    
        
    