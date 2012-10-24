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

from django.core.exceptions import ValidationError
from django.db import transaction

from ecm.apps.common import eveapi
from ecm.apps.common.models import Setting, APICall
from ecm.apps.corp.models import Corporation, Alliance
from ecm.apps.hr.models.member import Member
from ecm.lib import eveapi_patch
import re

eveapi_patch.patch_autocast()

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
@transaction.commit_on_success
def pull_character(charid):
    api_conn = eveapi.EVEAPIConnection()
    char = api_conn.eve.CharacterInfo(characterID = charid)
    try:
        corp = Corporation.objects.get(corporationID = char.corporationID)
    except Corporation.DoesNotExist:
        corp = pull_corporation(char.corporationID)
    mem = Member()
    mem.characterID = char.characterID
    mem.characterName = char.characterName
    mem.race = char.race
    mem.bloodline = char.bloodline
    mem.corp = corp
    mem.corpDate = char.corporationDate
    mem.securityStatus = char.securityStatus
    mem.save()
    return mem

#------------------------------------------------------------------------------
@transaction.commit_on_success
def pull_corporation(corporationID):
    api_conn = eveapi.EVEAPIConnection()
    corp_api = api_conn.corp.CorporationSheet(corporationID = corporationID)
    try:
        alliance = Alliance.objects.get(allianceID = corp_api.allianceID)
    except Alliance.DoesNotExist:
        alliance = pull_alliance(corp_api.allianceID)
    corp = Corporation()
    corp.alliance = alliance
    corp.corporationID = corp_api.corporationID
    corp.corporationName = corp_api.corporationName
    corp.ticker = corp_api.ticker
    corp.ceoID = corp_api.ceoID
    corp.ceoName = corp_api.ceoName
    corp.locationID = corp_api.stationID
    corp.location = corp_api.stationName
    corp.description = fix_description(corp_api.description)
    corp.taxRate = corp_api.taxRate
    corp.save()
    return corp

#------------------------------------------------------------------------------
@transaction.commit_on_success
def pull_alliance(allianceID):
    api_conn = eveapi.EVEAPIConnection()
    alliancesApi = api_conn.eve.AllianceList()
    alliance = Alliance()
    alliance.allianceID = allianceID
    for a in alliancesApi.alliances:
        if a.allianceID == allianceID:
            alliance.shortName = a.shortName
            alliance.name = a.name
            alliance.save()
            break
    return alliance

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
