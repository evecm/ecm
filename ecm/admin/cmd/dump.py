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
import subprocess
from optparse import OptionParser
from ConfigParser import SafeConfigParser

from ecm.lib.subcommand import Subcommand
from ecm.admin.cmd.load import CCP_DATA_DUMPS

#-------------------------------------------------------------------------------
def sub_command():
    # INIT
    dump_cmd = Subcommand('dump',
                          parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                          help='Dump patched EVE data to standard output.',
                          callback=run)
    return dump_cmd

#-------------------------------------------------------------------------------
def run(command, global_options, options, args):
    
    if not args:
        command.parser.error('Missing instance directory.')
    instance_dir = args.pop(0)
    
    config = SafeConfigParser()
    if config.read([os.path.join(instance_dir, 'settings.ini')]):
        db_engine = config.get('database', 'ecm_engine')
        db_name = config.get('database', 'ecm_name')
        db_user = config.get('database', 'ecm_user')
        db_password = config.get('database', 'ecm_password')
    else:
        command.parser.error('Could not read "settings.ini" in instance dir.')
    try:
        sql = CCP_DATA_DUMPS[db_engine]
    except KeyError:
        command.parser.error('Cannot dump patched EVE data with database engine %r. '
                             'Supported engines: %r' % (db_engine, CCP_DATA_DUMPS.keys()))
    
    sys.stdout.write("""BEGIN;

-- reset existing data
DELETE FROM eve_celestialobject WHERE x IS NOT NULL; -- to keep conquerable outposts
DELETE FROM eve_blueprintreq;
DELETE FROM eve_blueprinttype;
DELETE FROM eve_controltowerresource;
DELETE FROM eve_marketgroup;
DELETE FROM eve_type;
DELETE FROM eve_group;
DELETE FROM eve_category;

""")
    sys.stdout.flush()
    try:
        cmd = sql['DUMP'] % { 'user': db_user, 'password': db_password, 'name': db_name }
        os.environ['PGPASSWORD'] = db_password
        subprocess.call(cmd.split(), cwd=os.path.abspath(instance_dir))
    except KeyboardInterrupt:
        sys.stdout.write('\n')
        sys.exit(1)
    sys.stdout.write('COMMIT;\n\n')
