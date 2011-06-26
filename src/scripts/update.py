#!/usr/bin/env python

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

__date__ = "2010-05-17"
__author__ = "diabeteman"

import os, sys

scripts_dir = os.path.abspath(os.path.dirname(__file__))
install_dir = os.path.abspath(os.path.join(scripts_dir, "../"))
sys.path.append(install_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ecm.settings'

from ecm.core.parsers import *
from ecm.core.tasks import users

FUNCTIONS = {
    "assets" : assets.update,
    "corp" : corp.update,
    "member_roles" : membersecu.update,
    "members" : membertrack.update,
    "outposts" : outposts.update,
    "reftypes" : reftypes.update,
    "titles" : titles.update,
    "wallets" : wallets.update,
    "user_access" : users.update_all_users_accesses,
    "clean_unregistered_users" : users.cleanup_unregistered_users,
    "update_user_accesses" : users.update_all_users_accesses
}


if __name__ == "__main__":
    try:
        FUNCTIONS[sys.argv[1]]()
    except (IndexError, KeyError):
        print >>sys.stderr, "usage: update.py",
        func_names = FUNCTIONS.keys()
        func_names.sort()
        print >>sys.stderr, "{%s}" % "|".join(func_names)
        sys.exit(1)
