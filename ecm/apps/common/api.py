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

__date__ = '2012 5 15'
__author__ = 'diabeteman'

import re

from django.core.exceptions import ValidationError
from django.conf import settings

if settings.EVEAPI_STUB_ENABLED:
    from ecm.utils import eveapi_stub as eveapi  #@UnusedImport
    from ecm.utils.eveapi_stub import Error, ServerError, AuthenticationError, RequestError #@UnusedImport
else:
    from ecm.lib import eveapi  #@UnusedImport @Reimport
    from ecm.lib.eveapi import Error, ServerError, AuthenticationError, RequestError #@UnusedImport @Reimport

from ecm.apps.common.models import Setting, APICall
from ecm.apps.corp.models import Corporation



#------------------------------------------------------------------------------
EVE_API_VERSION = '2'
def check_version(version):
    if version != EVE_API_VERSION:
        raise DeprecationWarning("Wrong EVE API version. "
                "Expected '%s', got '%s'." % (EVE_API_VERSION, version))

#------------------------------------------------------------------------------
def get_api():
    keyID = Setting.get(name='common_api_keyID')
    vCode = Setting.get(name='common_api_vCode')
    if not keyID or not vCode:
        raise Setting.DoesNotExist('the settings "common_api_keyID" or "common_api_vCode" are empty')
    else:
        return keyID, vCode

#------------------------------------------------------------------------------
def get_charID():
    characterID = Setting.get(name='common_api_characterID')
    if not characterID:
        raise Setting.DoesNotExist('the setting "common_api_characterID" is empty')
    else:
        return characterID

#------------------------------------------------------------------------------
def set_api(keyID, vCode, characterID):
    Setting.objects.filter(name='common_api_keyID').update(value=repr(keyID))
    Setting.objects.filter(name='common_api_vCode').update(value=repr(vCode))
    Setting.objects.filter(name='common_api_characterID').update(value=repr(characterID))

#------------------------------------------------------------------------------
def connect(proxy=None):
    """
    Creates a connection to the web API with director credentials
    """
    conn = eveapi.EVEAPIConnection(proxy=proxy)
    keyID, vCode = get_api()
    return conn.auth(keyID=keyID, vCode=vCode)

#------------------------------------------------------------------------------
def connect_user(user_api, proxy=None):
    """
    Creates a connection to the web API with a user's credentials
    """
    conn = eveapi.EVEAPIConnection(proxy=proxy)
    return conn.auth(keyID=user_api.keyID, vCode=user_api.vCode)

#------------------------------------------------------------------------------
def required_access_mask(character=True):
    accessMask = 0
    key_type = character and APICall.CHARACTER or APICall.CORPORATION
    for call in APICall.objects.filter(type=key_type, required=True):
        accessMask |= call.mask
    return accessMask

#------------------------------------------------------------------------------
def check_access_mask(accessMask, character):
    missing = []
    key_type = character and APICall.CHARACTER or APICall.CORPORATION
    for call in APICall.objects.filter(type=key_type, required=True):
        if not accessMask & call.mask:
            missing.append(call)
    if missing:
        raise eveapi.AuthenticationError(0, "This API Key misses mandatory accesses: "
                                         + ', '.join([ call.name for call in missing ]))

#------------------------------------------------------------------------------
def validate_director_api_key(keyID, vCode):
    try:
        connection = eveapi.EVEAPIConnection().auth(keyID=keyID, vCode=vCode)
        response = connection.account.APIKeyInfo()
        if response.key.type.lower() != "corporation":
            raise ValidationError("Wrong API Key type '%s'. Please provide a Corporation API Key." % response.key.type)
        check_access_mask(response.key.accessMask, character=False)
    except eveapi.AuthenticationError, e:
        raise ValidationError(str(e))

    keyCharIDs = [ char.characterID for char in response.key.characters ]
    return keyCharIDs[0]

#------------------------------------------------------------------------------
class Character:
    name = ""
    characterID = 0
    corporationID = 0
    corporationName = "No Corporation"
    is_corped = False

def get_account_characters(user_api):
    connection = connect_user(user_api)
    response = connection.account.APIKeyInfo()
    corp = Corporation.objects.mine()
    characters = []
    if response.key.type.lower() != "account":
        raise eveapi.AuthenticationError(0, "Wrong API Key type '" + response.key.type + "'. " +
                                         "Please provide an API Key working for all characters of your account.")

    check_access_mask(response.key.accessMask, character=True)

    for char in response.key.characters:
        c = Character()
        c.name = char.characterName
        c.characterID = char.characterID
        c.corporationID = char.corporationID
        c.corporationName = char.corporationName
        c.is_corped = (char.corporationID == corp.corporationID)
        characters.append(c)
    return characters

#------------------------------------------------------------------------------
FONT_TAG_REGEXP = re.compile('</?font.*?>', re.DOTALL)
SPAN_TAG_REGEXP = re.compile('</?span.*?>', re.DOTALL)
def fix_description(description):
    # an empty corp description string ('<description />' )will throw a TypeError
    # so let's catch it
    try:
        desc, _ = FONT_TAG_REGEXP.subn("", description)
        desc, _ = SPAN_TAG_REGEXP.subn("", desc)
        return desc.strip()
    except TypeError:
        return '-'
