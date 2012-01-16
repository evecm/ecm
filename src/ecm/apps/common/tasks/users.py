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

__date__ = "2011 10 25"
__author__ = "diabeteman"

import logging

from django.db import transaction

from ecm.apps.common.models import RegistrationProfile

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def cleanup_unregistered_users():
    LOG.info("Deleting activation keys...")
    count = 0
    for profile in RegistrationProfile.objects.all():
        if profile.activation_key_expired():
            user = profile.user
            count += 1
            if user.is_active:
                # user has activated his/her account. we delete the activation key
                profile.delete()
            else:
                LOG.info("activation key has exprired for '%s', deleting user..." % user.username)
                user.delete() # this will delete the profile along with the user
    LOG.info("%d activation keys deleted" % count)
