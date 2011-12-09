# Copyright (c) 2010-2011 Robin Jarry
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.

# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2010-03-23"
__author__ = "diabeteman"

from ecm.lib import eveapi
from ecm.core.eve.validators import check_user_access_mask
from ecm.apps.common.models import Setting
from ecm.apps.corp.models import Corp

#------------------------------------------------------------------------------
def get_api():
    keyID = Setting.objects.get(name='common_api_keyID').getValue()
    vCode = Setting.objects.get(name='common_api_vCode').getValue()
    if not keyID or not vCode:
        raise Setting.DoesNotExist('the settings "common_api_keyID" or "common_api_vCode" are empty')
    else:
        return keyID, vCode

#------------------------------------------------------------------------------
def get_charID():
    characterID = Setting.objects.get(name='common_api_characterID').getValue()
    if not characterID:
        raise Setting.DoesNotExist('the setting "common_api_characterID" is empty')
    else:
        return characterID

#------------------------------------------------------------------------------
def set_api(keyID, vCode, characterID):
    Setting.objects.get_or_create(name='common_api_keyID').update(value=repr(keyID))
    Setting.objects.get_or_create(name='common_api_vCode').update(value=repr(vCode))
    Setting.objects.get_or_create(name='common_api_characterID').update(value=repr(characterID))

#------------------------------------------------------------------------------
def connect(proxy=None):
    """
    Creates a connection to the web API with director credentials
    """
    conn = eveapi.EVEAPIConnection(scheme="https", proxy=proxy)
    keyID, vCode = get_api()
    return conn.auth(keyID=keyID, vCode=vCode)

#------------------------------------------------------------------------------
def connect_user(user_api, proxy=None):
    """
    Creates a connection to the web API with a user's credentials
    """
    conn = eveapi.EVEAPIConnection(scheme="http", proxy=proxy)
    return conn.auth(keyID=user_api.keyID, vCode=user_api.vCode)


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
    corp = Corp.objects.get(id=1)
    characters = []
    if response.key.type.lower() != "account":
        raise eveapi.Error(0, "Wrong API Key type '" + response.key.type + "'. " +
                           "Please provide an API Key working for all characters of your account.")

    check_user_access_mask(response.key.accessMask)

    for char in response.key.characters:
        c = Character()
        c.name = char.characterName
        c.characterID = char.characterID
        c.corporationID = char.corporationID
        c.corporationName = char.corporationName
        c.is_corped = (char.corporationID == corp.corporationID)
        characters.append(c)
    return characters

