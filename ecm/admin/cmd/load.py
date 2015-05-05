# Copyright (c) 2010-2014 AUTHORS
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

__date__ = '2015 1 21'
__author__ = 'diabeteman'

import os
import shutil
import urllib2
import tempfile
from optparse import OptionParser
from ConfigParser import SafeConfigParser

from ecm.lib.subcommand import Subcommand
from ecm.admin.util import pipe_to_dbshell, expand
from ecm.admin.util import log
from ecm.admin.util import run_python_cmd


FUZZWORK_TABLES = [
    'invTypes',
    'invCategories',
    'invGroups',
    'invMarketGroups',
    'invMetaTypes',
    'invControlTowerResources',
    'mapDenormalize',
    'mapSolarSystems',
    'dgmTypeAttributes',
    'industryBlueprints',
    'industryActivity',
    'industryActivityProducts',
    'industryActivityMaterials',
    'industryActivityProbabilities',
]

FUZZWORK_URL_PREFIX = 'https://www.fuzzwork.co.uk/dump/latest/'
FUZZWORK_URL_SUFFIX = '.sql.bz2'
FUZZWORK_PATCH_SCRIPT = 'fuzzwork_patch_mysql.sql'

#-------------------------------------------------------------------------------
def sub_command():
    # INIT
    description = 'Load EVE static data into the instance database.  '\
                  'The data can be in Fuzzwork table format, or preconverted into ECM format.'
    
    load_cmd = Subcommand('load',
                          parser=OptionParser(usage='%prog [OPTIONS] instance_dir [dumppath]'),
                          help=description,
                          callback=run)
    load_cmd.parser.description = description + '  "dumppath" can be an URL or local path to a dump file (.SQL), optionally compressed as bz2, gz, or zip.  ' \
                                                'If the -f option is specified, "dumppath" is optional and refers to the location of the SDE table files.'
    load_cmd.parser.add_option('-f', '--fuzzwork',
                               dest='fuzzwork', default=False, action='store_true',
                               help='Download and load the EVE static data from the Fuzzwork website, default path is %s.  (MySQL only)' % FUZZWORK_URL_PREFIX)
    load_cmd.parser.add_option('--save', dest='save', default=False, action='store_true',
                               help='Save the downloaded file(s) to your current directory for later use.')

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
    
    if options.fuzzwork:
        if not 'mysql' in db_engine:
            command.parser.error('Fuzzwork download only supported with MySql database engine.')
        if args:
            dumppath = args.pop(0)
        else:
            dumppath = FUZZWORK_URL_PREFIX
    elif not args:
        command.parser.error('Missing dumppath or --fuzzwork option.')
    else:
        dumppath = args.pop(0)
    
    try:
        tempdir = tempfile.mkdtemp()
    
        if options.save:
            savedir = '.'
        else:
            savedir = tempdir
        
        if options.fuzzwork:
            for table in FUZZWORK_TABLES:
                load_dump_file(instance_dir, savedir, tempdir, os.path.join(dumppath, table) + FUZZWORK_URL_SUFFIX, db_engine, db_password)
            log('Patching CCP format SDE to match ours... (this also takes awhile)')
            pipe_to_dbshell(os.path.join(SQL_ROOT, FUZZWORK_PATCH_SCRIPT), instance_dir, password=db_password)
        else:
            load_dump_file(instance_dir, savedir, tempdir, dumppath, db_engine, db_password)        
        
        log('EVE static data successfully imported.')
    finally:
        log('Removing temp files...')
        shutil.rmtree(tempdir)
        log('done')

#-------------------------------------------------------------------------------
def load_dump_file(instance_dir, savedir, tempdir, datadump, db_engine, db_password):
    if not os.path.exists(datadump):
        # download from URL
        dump_archive = os.path.join(savedir, os.path.basename(datadump))
        log('Downloading %r to %r...', datadump, dump_archive)
        req = urllib2.urlopen(datadump)
        with open(dump_archive, 'wb') as fp:
            shutil.copyfileobj(req, fp)
        req.close()
    else:
        dump_archive = datadump
    
    extension = os.path.splitext(dump_archive)[-1]
    if extension in ('.bz2', '.gz', '.zip'):
        # decompress archive
        log('Expanding %r to %r...', dump_archive, tempdir)
        dump_file = expand(dump_archive, tempdir)
        extension = os.path.splitext(dump_file)[-1]
    else:
        dump_file = dump_archive
        
    log('Importing %r... (this may take awhile!)', dump_file)
    
    if extension in ('.json'):
        load_json_dump(instance_dir, dump_file, tempdir)
    elif 'sqlite' in db_engine:
        import sqlite3
        config = SafeConfigParser()
        db_dir = ''
        if config.read([os.path.join(instance_dir, 'settings.ini')]):
            db_dir = config.get('database', 'sqlite_db_dir')
        if not db_dir:
            db_dir = os.path.join(instance_dir, 'db')
            
        db_file = os.path.join(db_dir, 'ecm.sqlite')
        
        # Connect to the instance DB and attach the SDE
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()
        cursor.execute('ATTACH DATABASE \'%s\' AS "eve";' % dump_file)
        
        # Get the tables from the SDE (import them all)
        cursor.execute('SELECT "name","sql" FROM "eve"."sqlite_master" WHERE "type"="table" AND "sql" IS NOT NULL;')
        tables = cursor.fetchall()
        
        # Load the table data as brand new tables matching the dump file (to avoid unexplainable errors, maybe because Django/south doesn't set them up the same as the DB dump conversion scripts)
        for table in tables:
            tablename = table[0]
            tablesql  = table[1]
            
            # Drop and recreate the table
            cursor.execute('DROP TABLE "%s";' % tablename)
            cursor.execute(tablesql)
            
            # Insert the data
            cursor.execute('INSERT INTO "%s" SELECT * FROM "eve"."%s";' % (tablename, tablename))

        # Get the indicies of the attached DB and create them
        cursor.execute('SELECT "sql" FROM "eve"."sqlite_master" WHERE "type"="index" AND "sql" IS NOT NULL;')
        indicies = cursor.fetchall()
        for index in indicies:
            cursor.execute(index[0])
            
        cursor.execute('DETACH DATABASE "eve";')
        cursor.close()
        connection.commit()
    else:
        pipe_to_dbshell(dump_file, instance_dir, password=db_password)


#-------------------------------------------------------------------------------
def print_load_message(instance_dir, db_engine):
    
    if 'mysql' in db_engine:
        engine = 'mysql'
    elif 'sqlite' in db_engine:
        engine = 'sqlite'
    else:
        engine = 'psql'
    
    log('')
    log('Now you need to load your database with EVE static data.')
    log('Please execute `ecm-admin load %s <ecm_dump_file>` to do so.' % instance_dir)
    log('You will find links to official dump conversions here https://github.com/evecm/ecm/wiki/Static-Data')
    log('Be sure to take the latest one matching your db engine "%s".' % engine)

#-------------------------------------------------------------------------------
def load_json_dump(instance_dir, json_file, tempdir):
    # Break the load into multiple chunks to save memory
    # blocksize must be large enough to grab the main foreign keys in the first chunk
    blocksize = 15000000
    
    infile = open(json_file, 'r')
    outfilename = os.path.join(tempdir, 'temp.json')
    i = 1
    data = infile.read(blocksize)
    while(len(data)):
        outfile = open(outfilename, 'w')
        if (i > 1):
            outfile.write('[')
        outfile.write(data)
            
        if (len(data) == blocksize):
            # Look for "}," and separate there
            separator = 0
            while(separator < 2):
                databyte = infile.read(1)
                if (databyte == ']'):
                    separator = 2
                elif (databyte == '}'):
                    separator = 1
                elif (databyte == ',' and separator == 1):
                    separator = 2
                    databyte = ']'
                else:
                    separator = 0                 
                outfile.write(databyte)

        outfile.close()
        
        run_python_cmd(['manage.py', 'loaddata', os.path.abspath(outfilename)], run_dir=instance_dir)
        
        # If len is less than blocksize we're out of data
        if (len(data) < blocksize):
            break
        
        data = infile.read(blocksize)
        i = i + 1

    infile.close()
    os.remove(outfilename)
