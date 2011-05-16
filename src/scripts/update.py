# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2010-05-17"
__author__ = "diabeteman"

import os, sys

scripts_dir = os.path.abspath(os.path.dirname(__file__))
install_dir = os.path.abspath(os.path.join(scripts_dir, "../../"))
sys.path.append(install_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ecm.settings'

from ecm.core.parsers import assets, corp, membersecu, membertrack, outposts, reftypes, titles, wallets
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
