#!/usr/bin/env python

import MySQLdb, urllib2, json, base64

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
ECM_URL     = 'http://ecm.diabeteman.com'
ECM_USER    = '' # to complete
ECM_PASSWD  = '' # to complete
ECM_BINDING = 'forum'
ECM_GROUPS  = '/api/bindings/%s/groups' % ECM_BINDING
ECM_USERS   = '/api/bindings/%s/users' % ECM_BINDING

#------------------------------------------------------------------------------
def main():
    groups, users = fetch_ecm_data()
    managed_groups = tuple([g['external_id'] for g in groups])
    update_forum_access(managed_groups, users)

#------------------------------------------------------------------------------
def fetch_ecm_data():
    print 'Fetching info from ECM...',
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
    print 'done'
    return groups, users

#------------------------------------------------------------------------------
def update_forum_access(managed_groups, users):
    if not managed_groups or not users:
        print 'Nothing to update.'
        return
    try:
        print 'Updating database...',
        conn = MySQLdb.connect(host=DB_HOST, 
                             port=DB_PORT, 
                             user=DB_USER, 
                             passwd=DB_PASSWD, 
                             db=DB)
        
        cursor = conn.cursor()
        cursor.execute('LOCK TABLES `%s`.`%s` WRITE;' % (DB, DB_TABLES['user_groups']))
    
        cursor.execute('BEGIN;')
        cursor.execute('DELETE FROM `%s`.`%s` ' % (DB, DB_TABLES['user_groups']) + 
                       'WHERE group_id IN %s;', (managed_groups,))
        for u in users:
            update_user_access(u['external_id'], u['groups'], cursor) 
    
        cursor.execute('COMMIT;')
        cursor.execute('UNLOCK TABLES;')
        cursor.close()
        conn.commit()
        print 'commited modifications'
    except:
        conn.rollback()
        print 'rollbacked modifications'
        raise
#------------------------------------------------------------------------------
def update_user_access(user_id, groups, cursor):
    for g in groups:
        cursor.execute('INSERT INTO `%s`.`%s`(group_id, user_id, user_pending) ' % (DB, DB_TABLES['user_groups']) +
                       'VALUES (%s, %s, 0);', (g, user_id))

#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

