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

import re

SPECIAL_CHAR_RE = re.compile(r'\\x\w\w')

def fix_encoding(s):
    """
    Replace UTF-8 character codes by their actual value.

    example: '\\xE9' is replaced by unicode character '\xE9'
    """
    new_str, _ = SPECIAL_CHAR_RE.subn(repl_func, s)
    return unicode(new_str)

def repl_func(match):
    m = match.group(0)
    try:
        return CHAR_MAP[m]
    except KeyError:
        return m

CHAR_MAP = {
    '\\xa1': u'\xA1', '\\xA1': u'\xA1',
    '\\xa2': u'\xA2', '\\xA2': u'\xA2',
    '\\xa3': u'\xA3', '\\xA3': u'\xA3',
    '\\xa4': u'\xA4', '\\xA4': u'\xA4',
    '\\xa5': u'\xA5', '\\xA5': u'\xA5',
    '\\xa6': u'\xA6', '\\xA6': u'\xA6',
    '\\xa7': u'\xA7', '\\xA7': u'\xA7',
    '\\xa8': u'\xA8', '\\xA8': u'\xA8',
    '\\xa9': u'\xA9', '\\xA9': u'\xA9',
    '\\xaa': u'\xAA', '\\xAA': u'\xAA',
    '\\xab': u'\xAB', '\\xAB': u'\xAB',
    '\\xac': u'\xAC', '\\xAC': u'\xAC',
    '\\xad': u'\xAD', '\\xAD': u'\xAD',
    '\\xae': u'\xAE', '\\xAE': u'\xAE',
    '\\xaf': u'\xAF', '\\xAF': u'\xAF',
    '\\xb0': u'\xB0', '\\xB0': u'\xB0',
    '\\xb1': u'\xB1', '\\xB1': u'\xB1',
    '\\xb2': u'\xB2', '\\xB2': u'\xB2',
    '\\xb3': u'\xB3', '\\xB3': u'\xB3',
    '\\xb4': u'\xB4', '\\xB4': u'\xB4',
    '\\xb5': u'\xB5', '\\xB5': u'\xB5',
    '\\xb6': u'\xB6', '\\xB6': u'\xB6',
    '\\xb7': u'\xB7', '\\xB7': u'\xB7',
    '\\xb8': u'\xB8', '\\xB8': u'\xB8',
    '\\xb9': u'\xB9', '\\xB9': u'\xB9',
    '\\xba': u'\xBA', '\\xBA': u'\xBA',
    '\\xbb': u'\xBB', '\\xBB': u'\xBB',
    '\\xbc': u'\xBC', '\\xBC': u'\xBC',
    '\\xbd': u'\xBD', '\\xBD': u'\xBD',
    '\\xbe': u'\xBE', '\\xBE': u'\xBE',
    '\\xbf': u'\xBF', '\\xBF': u'\xBF',
    '\\xc0': u'\xC0', '\\xC0': u'\xC0',
    '\\xc1': u'\xC1', '\\xC1': u'\xC1',
    '\\xc2': u'\xC2', '\\xC2': u'\xC2',
    '\\xc3': u'\xC3', '\\xC3': u'\xC3',
    '\\xc4': u'\xC4', '\\xC4': u'\xC4',
    '\\xc5': u'\xC5', '\\xC5': u'\xC5',
    '\\xc6': u'\xC6', '\\xC6': u'\xC6',
    '\\xc7': u'\xC7', '\\xC7': u'\xC7',
    '\\xc8': u'\xC8', '\\xC8': u'\xC8',
    '\\xc9': u'\xC9', '\\xC9': u'\xC9',
    '\\xca': u'\xCA', '\\xCA': u'\xCA',
    '\\xcb': u'\xCB', '\\xCB': u'\xCB',
    '\\xcc': u'\xCC', '\\xCC': u'\xCC',
    '\\xcd': u'\xCD', '\\xCD': u'\xCD',
    '\\xce': u'\xCE', '\\xCE': u'\xCE',
    '\\xcf': u'\xCF', '\\xCF': u'\xCF',
    '\\xd0': u'\xD0', '\\xD0': u'\xD0',
    '\\xd1': u'\xD1', '\\xD1': u'\xD1',
    '\\xd2': u'\xD2', '\\xD2': u'\xD2',
    '\\xd3': u'\xD3', '\\xD3': u'\xD3',
    '\\xd4': u'\xD4', '\\xD4': u'\xD4',
    '\\xd5': u'\xD5', '\\xD5': u'\xD5',
    '\\xd6': u'\xD6', '\\xD6': u'\xD6',
    '\\xd7': u'\xD7', '\\xD7': u'\xD7',
    '\\xd8': u'\xD8', '\\xD8': u'\xD8',
    '\\xd9': u'\xD9', '\\xD9': u'\xD9',
    '\\xda': u'\xDA', '\\xDA': u'\xDA',
    '\\xdb': u'\xDB', '\\xDB': u'\xDB',
    '\\xdc': u'\xDC', '\\xDC': u'\xDC',
    '\\xdd': u'\xDD', '\\xDD': u'\xDD',
    '\\xde': u'\xDE', '\\xDE': u'\xDE',
    '\\xdf': u'\xDF', '\\xDF': u'\xDF',
    '\\xe0': u'\xE0', '\\xE0': u'\xE0',
    '\\xe1': u'\xE1', '\\xE1': u'\xE1',
    '\\xe2': u'\xE2', '\\xE2': u'\xE2',
    '\\xe3': u'\xE3', '\\xE3': u'\xE3',
    '\\xe4': u'\xE4', '\\xE4': u'\xE4',
    '\\xe5': u'\xE5', '\\xE5': u'\xE5',
    '\\xe6': u'\xE6', '\\xE6': u'\xE6',
    '\\xe7': u'\xE7', '\\xE7': u'\xE7',
    '\\xe8': u'\xE8', '\\xE8': u'\xE8',
    '\\xe9': u'\xE9', '\\xE9': u'\xE9',
    '\\xea': u'\xEA', '\\xEA': u'\xEA',
    '\\xeb': u'\xEB', '\\xEB': u'\xEB',
    '\\xec': u'\xEC', '\\xEC': u'\xEC',
    '\\xed': u'\xED', '\\xED': u'\xED',
    '\\xee': u'\xEE', '\\xEE': u'\xEE',
    '\\xef': u'\xEF', '\\xEF': u'\xEF',
    '\\xf0': u'\xF0', '\\xF0': u'\xF0',
    '\\xf1': u'\xF1', '\\xF1': u'\xF1',
    '\\xf2': u'\xF2', '\\xF2': u'\xF2',
    '\\xf3': u'\xF3', '\\xF3': u'\xF3',
    '\\xf4': u'\xF4', '\\xF4': u'\xF4',
    '\\xf5': u'\xF5', '\\xF5': u'\xF5',
    '\\xf6': u'\xF6', '\\xF6': u'\xF6',
    '\\xf7': u'\xF7', '\\xF7': u'\xF7',
    '\\xf8': u'\xF8', '\\xF8': u'\xF8',
    '\\xf9': u'\xF9', '\\xF9': u'\xF9',
    '\\xfa': u'\xFA', '\\xFA': u'\xFA',
    '\\xfb': u'\xFB', '\\xFB': u'\xFB',
    '\\xfc': u'\xFC', '\\xFC': u'\xFC',
    '\\xfd': u'\xFD', '\\xFD': u'\xFD',
    '\\xfe': u'\xFE', '\\xFE': u'\xFE',
    '\\xff': u'\xFF', '\\xFF': u'\xFF',
}

