# Copyright (c) 2010-2011 Robin Jarry
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

__date__ = "2011 9 2"
__author__ = "diabeteman"

from django.core.exceptions import ValidationError
from ecm.lib import eveapi



#------------------------------------------------------------------------------
USER_API_KEY_ACCESS_MASKS = {
    1 << 0: "AccountBalance",
    1 << 1: "AssetList",
    1 << 2: "CalendarEventAttendees",
    1 << 3: "CharacterSheet",
    1 << 4: "ContactList",
    1 << 5: "ContactNotifications",
    1 << 6: "FacWarStats",
    1 << 7: "IndustryJobs",
    1 << 8: "KillLog",
    1 << 9: "MailBodies",
    1 << 10: "MailingLists",
    1 << 11: "MailMessages",
    1 << 12: "MarketOrders",
    1 << 13: "Medals",
    1 << 14: "Notifications",
    1 << 15: "NotificationTexts",
    1 << 16: "Research",
    1 << 17: "SkillInTraining",
    1 << 18: "SkillQueue",
    1 << 19: "Standings",
    1 << 20: "UpcomingCalendarEvents",
    1 << 21: "WalletJournal",
    1 << 22: "WalletTransactions",
    1 << 23: "PublicCharacterInfo",
    1 << 24: "PrivateCharacterInfo",
    1 << 25: "AccountStatus",
    1 << 26: "Contracts",
}
CORP_API_KEY_ACCESS_MASKS = {
    1 << 0:  "AccountBalance",
    1 << 1:  "AssetList",
    1 << 2:  "MemberMedals",
    1 << 3:  "CorporationSheet",
    1 << 4:  "ContactList",
    1 << 5:  "ContainerLog",
    1 << 6:  "FacWarStats",
    1 << 7:  "IndustryJobs",
    1 << 8:  "KillLog",
    1 << 9:  "MemberSecurity",
    1 << 10: "MemberSecurityLog",
    1 << 11: "MemberTracking",
    1 << 12: "MarketOrders",
    1 << 13: "Medals",
    1 << 14: "OutpostList",
    1 << 15: "OutpostServiceDetail",
    1 << 16: "Shareholders",
    1 << 17: "StarbaseDetail",
    1 << 18: "Standings",
    1 << 19: "StarbaseList",
    1 << 20: "WalletJournal",
    1 << 21: "WalletTransactions",
    1 << 22: "Titles",
    1 << 23: "Contracts",
}

MANDATORY_CORP_API_ACCESS_MASKS = [
    1 << 1, # AssetList
    1 << 3, # CorporationSheet
    1 << 9, # MemberSecurity
    1 << 11, # MemberTracking
    1 << 14, # OutpostList
    1 << 20, # WalletJournal
    1 << 22, # Titles
]
MANDATORY_USER_API_ACCESS_MASKS = [
    1 << 3, # CharacterSheet
    1 << 23, # PublicCharacterInfo
    1 << 24, # PrivateCharacterInfo
]

#------------------------------------------------------------------------------
def user_access_mask():
    accessMask = 0
    for mask in MANDATORY_USER_API_ACCESS_MASKS:
        accessMask |= mask
    return accessMask

#------------------------------------------------------------------------------
def check_user_access_mask(accessMask):
    missing = []
    for mask in MANDATORY_USER_API_ACCESS_MASKS:
        if not accessMask & mask:
            missing.append(mask)
    if missing:
        raise eveapi.Error(0, "This API Key misses mandatory accesses: "
                           + ', '.join([ USER_API_KEY_ACCESS_MASKS[m] for m in missing ]))

#------------------------------------------------------------------------------
def check_corp_access_mask(accessMask):
    missing = []
    for mask in MANDATORY_CORP_API_ACCESS_MASKS:
        if not accessMask & mask:
            missing.append(mask)
    if missing:
        raise eveapi.Error(0, "This API Key misses mandatory accesses: "
                           + ', '.join([ CORP_API_KEY_ACCESS_MASKS[m] for m in missing ]))

#------------------------------------------------------------------------------
def validate_director_api_key(api_key):
    try:
        connection = eveapi.EVEAPIConnection().auth(keyID=api_key.keyID, vCode=api_key.vCode)
        response = connection.account.APIKeyInfo()
        if response.key.type.lower() != "corporation":
            raise ValidationError("Wrong API Key type '%s'. Please provide a Corporation API Key." % response.key.type)
        check_corp_access_mask(response.key.accessMask)
    except eveapi.Error, e:
        raise ValidationError(str(e))

    keyCharIDs = [char.characterID for char in response.key.characters]
    if api_key.characterID not in keyCharIDs:
        raise ValidationError("Wrong characterID provided, API Key has %s" % str(keyCharIDs))
