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

from __future__ import with_statement

__date__ = '2012 5 18'
__author__ = 'diabeteman'

import os
import bz2
import shutil
import urllib2
import tempfile
from optparse import OptionParser
from ConfigParser import SafeConfigParser

from ecm.lib.subcommand import Subcommand
from ecm.admin.util import pipe_to_dbshell
from ecm.admin.util import log


CCP_DATA_DUMPS = {
    'django.db.backends.postgresql_psycopg2': {
        'URL': 'http://zofu.no-ip.de/esc10/esc10-pgsql-v1.sql.bz2',
        'PATCH': 'eve_ecm_patch_psql.sql',
        'DROP': 'drop_eve_tables_psql.sql',
        'DUMP': 'pg_dump --user %(user)s --data-only --disable-triggers --table eve_* %(name)s',
    },
    'django.db.backends.mysql': {
        'URL': 'http://zofu.no-ip.de/esc10/esc10-sqlite3-v1.db.bz2',
        'PATCH': 'eve_ecm_patch_sqlite.sql',
        'DROP': None,
        'DUMP': 'drop_non_eve_tables.sql',
    },
}


#-------------------------------------------------------------------------------
def sub_command():
    # INIT
    load_cmd = Subcommand('load',
                          parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                          help='Load official EVE data dump into the instance database.',
                          callback=run)
    load_cmd.parser.add_option('-u', '--ccp-dump-url',
                               dest='ccp_dump_url',
                               help='URL where to download CCP official dump.')
    load_cmd.parser.add_option('-a', '--ccp-dump-archive',
                               dest='ccp_dump_archive',
                               help='Local archive of CCP official dump (skips download).')
    load_cmd.parser.add_option('-s', '--ccp-dump-sql',
                               dest='ccp_dump_sql',
                               help='Local SQL file of CCP official dump (skips decompression).')
    return load_cmd

#-------------------------------------------------------------------------------
SQL_ROOT = os.path.abspath(os.path.dirname(__file__))
def run(command, global_options, options, args):
    
    if not args:
        command.parser.error('Missing instance directory.')
    instance_dir = args.pop(0)
    
    config = SafeConfigParser()
    if config.read([os.path.join(instance_dir, 'settings.ini')]):
        db_engine = config.get('database', 'ecm_engine')
        db_password = config.get('database', 'ecm_password')
    else:
        command.parser.error('Could not read "settings.ini" in instance dir.')
    try:
        sql = CCP_DATA_DUMPS[db_engine]
    except KeyError:
        command.parser.error('Cannot load datadump with database engine %r. '
                             'Supported engines: %r' % (db_engine, CCP_DATA_DUMPS.keys()))

    try:
        tempdir = tempfile.mkdtemp()
        if not options.ccp_dump_sql:
            if not options.ccp_dump_archive:
                # download from URL
                url = options.ccp_dump_url or sql['URL']
                options.ccp_dump_archive = os.path.join(tempdir, os.path.basename(url))
                log('Downloading EVE original dump from %s to %s...', url, options.ccp_dump_archive)
                req = urllib2.urlopen(url)
                with open(options.ccp_dump_archive, 'wb') as fp:
                    shutil.copyfileobj(req, fp)
                req.close()
                log('Download complete.')
            # decompress archive
            options.ccp_dump_sql, _ = os.path.splitext(options.ccp_dump_archive)
            options.ccp_dump_sql = os.path.join(tempdir, os.path.basename(options.ccp_dump_sql))
            log('Expanding %s to %s...', options.ccp_dump_archive, options.ccp_dump_sql)
            bz_file_desc = bz2.BZ2File(options.ccp_dump_archive, 'rb')
            with open(options.ccp_dump_sql, 'wb') as db_file_desc:
                shutil.copyfileobj(bz_file_desc, db_file_desc)
            bz_file_desc.close()
            log('Expansion complete.')
        
        pipe_to_dbshell(options.ccp_dump_sql, instance_dir, password=db_password)
        pipe_to_dbshell(os.path.join(SQL_ROOT, sql['PATCH']), instance_dir, password=db_password)
        pipe_to_dbshell(os.path.join(SQL_ROOT, sql['DROP']), instance_dir, password=db_password)
        
        log('EVE data successfully imported.')
    finally:
        log('Removing temp files...')
        shutil.rmtree(tempdir)
        log('done')
    