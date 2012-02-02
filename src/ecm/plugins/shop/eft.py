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

__date__ = "2012 1 27"
__author__ = "diabeteman"

import re

HEADER = re.compile(r'\[(?P<ship>.+),.*')
ITEM = re.compile(r'^(?P<item>\w[^,\n]+)(,\s+(?P<charge>(.*)))?$', re.MULTILINE)
STACK = re.compile(r'(.*)\s+x(\d+)')

#------------------------------------------------------------------------------
def parse_export(export):
    """
    Parse an EFT export text block.
    Returns a dictionnary containing the items and their quantities.

    >>> test = '''[Hurricane, test]
    ... Tracking Enhancer II
    ... Tracking Enhancer II
    ... Damage Control II
    ... Gyrostabilizer II
    ... Gyrostabilizer II
    ... Reactor Control Unit II
    ...
    ... Y-T8 Overcharged Hydrocarbon I Microwarpdrive
    ... Sensor Booster II
    ... Large Shield Extender II
    ... Invulnerability Field II
    ...
    ... 720mm Howitzer Artillery II, Republic Fleet Depleted Uranium M
    ... 720mm Howitzer Artillery II, Republic Fleet Depleted Uranium M
    ... 720mm Howitzer Artillery II, Republic Fleet Depleted Uranium M
    ... 720mm Howitzer Artillery II, Republic Fleet Depleted Uranium M
    ... 720mm Howitzer Artillery II, Republic Fleet Depleted Uranium M
    ... 720mm Howitzer Artillery II, Republic Fleet Depleted Uranium M
    ... Assault Missile Launcher II, Caldari Navy Flameburst Light Missile
    ... Assault Missile Launcher II, Caldari Navy Flameburst Light Missile
    ...
    ... Medium Anti-EM Screen Reinforcer I
    ... Medium Anti-EM Screen Reinforcer I
    ... Medium Anti-Thermal Screen Reinforcer I
    ...
    ...
    ... Warrior II x5
    ... Warrior II x1'''
    >>> parse_export(test)
    {'Gyrostabilizer II': 2, 'Sensor Booster II': 1, 'Assault Missile Launcher II': 2, 'Tracking Enhancer II': 2, 'Reactor Control Unit II': 1, 'Hurricane': 1, 'Invulnerability Field II': 1, 'Caldari Navy Flameburst Light Missile': 2, 'Medium Anti-Thermal Screen Reinforcer I': 1, 'Y-T8 Overcharged Hydrocarbon I Microwarpdrive': 1, 'Warrior II': 6, 'Republic Fleet Depleted Uranium M': 6, 'Damage Control II': 1, '720mm Howitzer Artillery II': 6, 'Large Shield Extender II': 1, 'Medium Anti-EM Screen Reinforcer I': 2}
    """
    all_items = {}
    export = export.replace('\r\n', '\n')
    match = HEADER.search(export)
    if match:
        all_items[match.groupdict()['ship']] = 1
    for match in ITEM.finditer(export):
        item = match.groupdict()['item'].strip()

        match_stack = STACK.search(item)
        if match_stack:
            item = match_stack.group(1)
            stack = int(match_stack.group(2))
        else:
            stack = 1

        if all_items.has_key(item):
            all_items[item] += stack
        else:
            all_items[item] = stack

        if match.groupdict()['charge'] is not None:
            charge = match.groupdict()['charge']
            if all_items.has_key(charge):
                all_items[charge] += 1
            else:
                all_items[charge] = 1
    return all_items
