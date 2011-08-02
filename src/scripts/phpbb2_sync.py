#!/usr/bin/env python
'''
This script allows the synchronization of PHPBB2 user groups with ECM groups.

You must have previously set up a binding for your forum in ECM:

    - Add one binding per user you want to sync
    - Add one binding per group you want to sync


'''
import MySQLdb
import urllib2
import json
import base64
import logging
import os
from os import path
from logging import handlers

#------------------------------------------------------------------------------
# database connection info
DB_HOST     = 'localhost'
DB_PORT     = 3306
DB_USER     = '' # to complete
DB_PASSWD   = '' # to complete
DB          = ''
DB_TABLES   = {'groups'      : 'iceforum_groups', 
               'users'       : 'iceforum_user', 
               'user_groups' : 'iceforum_user_group'}
#------------------------------------------------------------------------------
# ECM connection info
ECM_URL     = 'http://ecm.yourserver.com'
ECM_USER    = '' # to complete
ECM_PASSWD  = '' # to complete
ECM_BINDING = 'forum'
ECM_GROUPS  = '/api/bindings/%s/groups' % ECM_BINDING
ECM_USERS   = '/api/bindings/%s/users' % ECM_BINDING

#------------------------------------------------------------------------------
# logging settings
LOG_DIR = '/var/log'
LOG_FILE = 'ecm_forum_sync.log'
if not path.exists(LOG_DIR): os.makedirs(LOG_DIR)
logger = logging.getLogger(__file__)
hdlr = handlers.TimedRotatingFileHandler(path.join(LOG_DIR, LOG_FILE), backupCount=15, when='midnight')
#hdlr = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)-5s] %(name)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

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
                             db=DB)
        cursor = conn.cursor()
        logger.debug('Locking table "%s"...' % DB_TABLES['user_groups'])
        cursor.execute('LOCK TABLES `%s`.`%s` WRITE;' % (DB, DB_TABLES['user_groups']))
    
        cursor.execute('BEGIN;')
        cursor.execute('DELETE FROM `%s`.`%s` ' % (DB, DB_TABLES['user_groups']) + 
                       'WHERE group_id IN %s;', (managed_groups,))
        for u in users:
            update_user_access(u['external_id'], u['groups'], cursor) 
            logger.debug('Updated user %s (%s) with groups %s', u['external_name'], str(u['external_id']), str(u['groups']))
        
        logger.debug('Committing modifications to the database...')
        cursor.execute('COMMIT;')
        logger.debug('Unlocking tables...')
        cursor.execute('UNLOCK TABLES;')
        cursor.close()
        conn.commit()
        logger.info('UPDATE SUCCESSFUL')
    except:
        if conn is not None: 
            conn.rollback()
            logger.warning('Rollbacked modifications')
        raise
#------------------------------------------------------------------------------
def update_user_access(user_id, groups, cursor):
    for g in groups:
        cursor.execute('INSERT INTO `%s`.`%s`(group_id, user_id, user_pending) ' % (DB, DB_TABLES['user_groups']) +
                       'VALUES (%s, %s, 0);', (g, user_id))


#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

