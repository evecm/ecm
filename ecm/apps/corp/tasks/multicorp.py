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

import zlib
import logging
import urlparse

from ecm.utils.http import HttpClient
from ecm.utils import crypto 
from ecm.apps.corp.models import Corporation, SharedData
from ecm.utils import _json as json


LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def update_all():
    corps = Corporation.objects.exclude(public_key='').exclude(public_key=None)
    for corp in corps.filter(is_trusted=True):
        LOG.debug('Updating info from corp: %s' % corp.ecm_url)
        update_one_corp(corp)

#------------------------------------------------------------------------------
def update_one_corp(corp):
    
    my_corp = Corporation.objects.mine()
    
    auth_url = urlparse.urljoin(corp.ecm_url, '/corp/auth/startsession/')
    client = HttpClient()
    
    LOG.debug('Establishing secure data exchange with %r...' % corp.ecm_url)
    response = client.get(auth_url, headers={'Authorization': 'RSA %s' % my_corp.key_fingerprint})
    cipher_txt_in = response.read()
    
    # we decrypt the response with our private key
    session_secret = crypto.rsa_decrypt(my_corp.private_key, cipher_txt_in)
    # and encrypt it back with the corp's public key
    cipher_txt_out = crypto.rsa_encrypt(corp.public_key, session_secret)
    
    # then send it to the server
    client.post(auth_url, cipher_txt_out)

    LOG.debug('Fetching which data %r is sharing with us...' % corp)
    # now we fetch the urls we're allowed to pull from this corporation
    response = client.get(urlparse.urljoin(corp.ecm_url, '/corp/share/allowed/'))
    data = crypto.aes_decrypt(session_secret, response.read())
    allowed_urls = json.loads(data)

    if not allowed_urls:
        LOG.warning('%r is not sharing any data with us' % corp.corporationName)
    for url in allowed_urls:
        try:
            shared_data = SharedData.objects.get(url=url)
            
            LOG.debug('Fetching shared data %r...' % url)
            response = client.get(urlparse.urljoin(corp.ecm_url, shared_data.url))
            
            raw_data = crypto.aes_decrypt(session_secret, response.read())
            
            if response.info().getheader('content-type') == 'application/gzip-compressed':
                raw_data = zlib.decompress(raw_data)
            
            shared_data.call_handler(corp, json.loads(raw_data))
        except SharedData.DoesNotExist:
            LOG.error('Unknown SharedData with url=%r' % url)
        except:
            LOG.exception('')
    
    LOG.debug('Ending secure session with %r...' % corp.ecm_url)
    # finally destroy our session info to be sure nobody will steal it :)
    client.get(urlparse.urljoin(corp.ecm_url, '/corp/auth/endsession/'))
    
