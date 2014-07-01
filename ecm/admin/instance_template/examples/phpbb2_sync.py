#!/usr/bin/env python
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

'''
This script allows the synchronization of PHPBB2 user groups with ECM groups.

You must have previously set up a binding for your forum in ECM.

Please read http://eve-corp-management.org/projects/ecm/wiki/ExternalAppsSync
for installation instructions.
'''
import os
from os import path
import sys
import base64
import urllib2
import MySQLdb
import logging
from logging import handlers

from ecm.utils import _json as json

#------------------------------------------------------------------------------
# database connection info
DB_HOST     = 'localhost'
DB_PORT     = 3306
DB_USER     = '' # to complete
DB_PASSWD   = '' # to complete
DB_NAME     = ''
DB_TABLES   = {'groups'      : 'forumprefix_groups',
               'users'       : 'forumprefix_user',
               'user_groups' : 'forumprefix_user_group'}
#------------------------------------------------------------------------------
# ECM connection info
ECM_URL     = 'http://ecm.yourserver.com'
ECM_USER    = '' # to complete
ECM_PASSWD  = '' # to complete
ECM_BINDING = 'forum'
ECM_GROUPS  = '/api/bindings/%s/groups/' % ECM_BINDING
ECM_USERS   = '/api/bindings/%s/users/' % ECM_BINDING

#------------------------------------------------------------------------------
# logging settings
LOG_DIR = path.abspath(path.join(path.abspath(path.dirname(__file__)), '../logs'))
LOG_FILE = 'ecm_forum_sync.log'
if not path.exists(LOG_DIR): os.makedirs(LOG_DIR)
logger = logging.getLogger()
hdlr = handlers.TimedRotatingFileHandler(path.join(LOG_DIR, LOG_FILE), backupCount=15, when='midnight')
#hdlr = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)-5s] %(message)s')
hdlr.setFormatter(formatter)
hdlr.setLevel(logging.INFO)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

#------------------------------------------------------------------------------
def main():
    try:
        groups, users = fetch_ecm_data()
        managed_groups = tuple([g['external_id'] for g in groups])
        update_forum_access(managed_groups, users)
    except:
        logger.exception('')
        exit(1)

#------------------------------------------------------------------------------
def fetch_ecm_data():
    logger.debug('Fetching info from ECM...')
    base64string = base64.encodestring('%s:%s' % (ECM_USER, ECM_PASSWD)).replace('\n', '')

    request = urllib2.Request(ECM_URL + ECM_GROUPS)
    request.add_header("Authorization", "Basic %s" % base64string)
    response = urllib2.urlopen(request)
    groups = json.loads(response.read())
    response.close()

    request = urllib2.Request(ECM_URL + ECM_USERS)
    request.add_header("Authorization", "Basic %s" % base64string)
    response = urllib2.urlopen(request)
    users = json.loads(response.read())
    response.close()
    logger.info('Fetched %d groups and %d users from ECM' % (len(groups), len(users)))
    return groups, users

#------------------------------------------------------------------------------
SQL_LOCK = 'LOCK TABLES `%s`.`%s` WRITE;' % (DB_NAME, DB_TABLES['user_groups'])
SQL_UNLOCK = 'UNLOCK TABLES;'
SQL_BEGIN = 'BEGIN;'
SQL_COMMIT = 'COMMIT;'
SQL_CLEAN_MANAGED_GROUPS = '''DELETE FROM `%s`.`%s`
WHERE `group_id` IN %%s;''' % (DB_NAME, DB_TABLES['user_groups'])
SQL_ADD_USER_TO_GROUP = '''insert into `%s`.`%s`(group_id, user_id, user_pending)
values (%%s, %%s, 0);''' % (DB_NAME, DB_TABLES['user_groups'])
SQL_RESET_DEFAULT_GROUPS = '''UPDATE `%s`.`%s`
SET `group_id` = 3 WHERE `group_id` IN %%s;''' % (DB_NAME, DB_TABLES['users'])

def update_forum_access(managed_groups, users):
    if not managed_groups or not users:
        logger.info('Nothing to update.')
        return
    try:
        logger.debug('Updating database...')
        conn = None
        conn = MySQLdb.connect(host=DB_HOST,
                             port=DB_PORT,
                             user=DB_USER,
                             passwd=DB_PASSWD,
                             db=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(SQL_LOCK)
        logger.debug('Locked table "%s"' % DB_TABLES['user_groups'])

        cursor.execute(SQL_BEGIN)
        cursor.execute(SQL_CLEAN_MANAGED_GROUPS, (managed_groups,))
        cursor.execute(SQL_RESET_DEFAULT_GROUPS, (managed_groups,))
        logger.info('Removed all users from groups %s' % str(managed_groups))
        for u in users:
            ext_id = u['external_id']
            name = u['external_name']
            groups = u['groups']
            for g in groups:
                cursor.execute(SQL_ADD_USER_TO_GROUP, (g, ext_id))
            logger.info('Updated user %s (%s) with groups %s', name, str(ext_id), str(groups))

        logger.debug('Committing modifications to the database...')
        cursor.execute(SQL_COMMIT)
        cursor.execute(SQL_UNLOCK)
        logger.debug('Unlocked tables')
        cursor.close()
        conn.commit()
        logger.info('UPDATE SUCCESSFUL')
    except:
        if conn is not None:
            conn.rollback()
            logger.warning('Rollbacked modifications')
        raise

#------------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'verbose':
        logger.setLevel(logging.DEBUG)
    main()
