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
from ecm.data.roles.models import CharacterOwnership, Title
from django.conf import settings

__date__ = "2011-03-14"
__author__ = "diabeteman"


import logging

from django.db import transaction
from django.contrib.auth.models import User, Group

from ecm.data.scheduler.models import GarbageCollector
from ecm.data.common.models import RegistrationProfile

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_manually
def collect_garbage():
    try:
        count = 0
        for collector in GarbageCollector.objects.all():
            logger.info("collecting old records for model: %s" % collector.db_table)
            model = collector.get_model()
            count = model.objects.all().count()
            
            if count > collector.min_entries_threshold:
                entries = model.objects.filter(date__lt=collector.get_expiration_date())
                for entry in entries:
                    entry.delete()
                
                deleted_entries = entries.count()
            else:
                deleted_entries = 0
            
            logger.info("%d entries will be deleted" % deleted_entries)    
            count += deleted_entries
        
        logger.debug("commiting modifications to database...")
        transaction.commit()
        logger.info("%d old records deleted" % count)
    except:
        # error catched, rollback changes
        transaction.rollback()
        logger.exception("cleanup failed")
        raise
    
#------------------------------------------------------------------------------
@transaction.commit_manually
def cleanup_unregistered_users():
    try:
        logger.info("Deleting unregistered users...")
        count = 0
        for profile in RegistrationProfile.objects.all():
            if profile.activation_key_expired():
                user = profile.user
                count += 1
                if not user.is_active:
                    logger.debug("activation key has exprired for '%s', deleting user..." % user.username)
                    user.delete()
                else:
                    # user has activated his/her account. we delete the activation key
                    profile.delete()
        logger.debug("commiting modifications to database...")
        transaction.commit()
        logger.info("%d unregistered users deleted")
    except:
        # error catched, rollback changes
        transaction.rollback()
        logger.exception("cleanup failed")
        raise

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_user_accesses():
    try:
        logger.info("Updating user accesses from their in-game roles...")
        for user in User.objects.all():
            owned = CharacterOwnership.objects.filter(user=user)
            titles = Title.objects.none()
            director = False
            for char in owned:
                director = char.character.is_director() or director
                titles |= char.character.getTitles()
            ids = titles.distinct().values_list("titleID", flat=True)
            user.groups.clear()
            for id in ids:
                user.groups.add(Group.objects.get(id=id))
            if director:
                user.groups.add(Group.objects.get(id=settings.DIRECTOR_GROUP_ID))
        logger.debug("commiting modifications to database...")
        transaction.commit()
        logger.info("User accesses updated")
    except:
        # error catched, rollback changes
        transaction.rollback()
        logger.exception("update failed")
        raise


