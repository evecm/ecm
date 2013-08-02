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


__date__ = '2012 5 18'
__author__ = 'diabeteman'

import os
import sys
import shutil
from optparse import OptionParser
from ConfigParser import SafeConfigParser

from ecm.admin.util import pipe_to_dbshell, log, run_command
from ecm.lib.subcommand import Subcommand

SUPPORTED_ENGINES = [
    'django.db.backends.postgresql_psycopg2',
    'django.db.backends.mysql',
    'django.db.backends.sqlite3',
]

#-------------------------------------------------------------------------------
def sub_command():
    # INIT
    dump_cmd = Subcommand('dump',
                          parser=OptionParser(usage='%prog [OPTIONS] instance_dir dump_file'),
                          help='Dump patched EVE data to a file.',
                          callback=run)
    dump_cmd.parser.add_option('-o', '--overwrite',
                               dest='overwrite', default=False, action='store_true',
                               help='Force overwrite any existing file.')
    return dump_cmd

#-------------------------------------------------------------------------------
def run(command, global_options, options, args):

    if not args:
        command.parser.error('Missing instance directory.')
    instance_dir = args.pop(0)
    if not args:
        command.parser.error('Missing dump file.')
    dump_file = args.pop(0)

    if not options.overwrite and os.path.exists(dump_file):
        command.parser.error('Dump file already exists.')

    config = SafeConfigParser()
    if config.read([os.path.join(instance_dir, 'settings.ini')]):
        db_engine = config.get('database', 'ecm_engine')
        db_name = config.get('database', 'ecm_name')
        db_user = config.get('database', 'ecm_user')
        db_password = config.get('database', 'ecm_password')
    else:
        command.parser.error('Could not read "settings.ini" in instance dir.')

    if not db_engine in SUPPORTED_ENGINES:
        command.parser.error('Cannot dump patched EVE data with database engine %r. '
                             'Supported engines: %r' % (db_engine, SUPPORTED_ENGINES))

    # remove existing file
    if os.path.exists(dump_file):
        os.remove(dump_file)

    log('Dumping EVE data to %r...' % dump_file)
    if 'postgresql' in db_engine:
        dump_psql(instance_dir, dump_file, db_user, db_password, db_name)
    elif 'mysql' in db_engine:
        dump_mysql(instance_dir, dump_file, db_user, db_password, db_name)
    elif 'sqlite' in db_engine:
        dump_sqlite(instance_dir, dump_file)
    log('EVE data successfully exported')

#-------------------------------------------------------------------------------
def dump_psql(instance_dir, dump_file, db_user, db_password, db_name):

    os.environ['PGDATABASE'] = db_name
    os.environ['PGUSER'] = db_user
    os.environ['PGPASSWORD'] = db_password

    tables = [ t for t in pipe_to_dbshell(r"\dt eve_*", instance_dir).split() if t.startswith('eve_') ]

    f = open(dump_file, 'w')
    try:
        try:
            dump_cmd = 'pg_dump --format=p --encoding=utf-8 --no-owner --no-privileges '\
                       '--quote-all-identifiers --data-only --disable-triggers --table eve_*'

            f.write('BEGIN;\n\n')
            for t in tables:
                f.write('TRUNCATE TABLE `%s`;\n' % t)
            f.write('\n')
            f.flush()
            run_command(dump_cmd.split(), os.path.abspath(instance_dir), stdout=f)
            f.flush()
            f.write('COMMIT;\n\n')
        except KeyboardInterrupt:
            f.close()
            sys.exit(1)
    finally:
        f.close()

#-------------------------------------------------------------------------------
MYSQL_DUMP_CMD = 'mysqldump --no-create-info --default-character-set=utf8 --disable-keys '\
                 '--user=%(user)s --password=%(password)s %(database)s %(tables)s'
def dump_mysql(instance_dir, dump_file, db_user, db_password, db_name):

    tables = [ t for t in pipe_to_dbshell(r"SHOW TABLES LIKE 'eve\_%';", instance_dir).split() if t.startswith('eve_') ]

    f = open(dump_file, 'w')
    try:
        try:
            dump_cmd = MYSQL_DUMP_CMD % {
                'user': db_user,
                'password': db_password,
                'database': db_name,
                'tables': ' '.join(tables)
            }
            f.write('BEGIN;\n\n')
            f.write('SET FOREIGN_KEY_CHECKS = 0;\n\n')
            for t in tables:
                f.write('TRUNCATE TABLE `%s`;\n' % t)
            f.write('\n')
            f.flush()
            run_command(dump_cmd.split(), os.path.abspath(instance_dir), stdout=f)
            f.flush()
            f.write('SET FOREIGN_KEY_CHECKS = 1;\n\n')
            f.write('COMMIT;\n\n')
        except KeyboardInterrupt:
            f.close()
            sys.exit(1)
    finally:
        f.close()

#-------------------------------------------------------------------------------
def dump_sqlite(instance_dir, dump_file):

    shutil.copy(os.path.join(instance_dir, 'db/ecm.sqlite'), dump_file)

    tables = [ (t,) for t in pipe_to_dbshell('.tables', instance_dir).split() if not t.startswith('eve_') ]

    import sqlite3
    connection = sqlite3.connect(dump_file)
    cursor = connection.cursor()
    for table in tables:
        cursor.execute('DROP TABLE "%s";' % table)
    cursor.execute('VACUUM;')
    cursor.close()
    connection.commit()
    connection.close()

