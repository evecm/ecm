#!/usr/bin/env python
import logging

# Copyright (c) 2010-2011 Robin Jarry
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

__date__ = "2011-06-17"
__author__ = "diabeteman"

import bz2, tempfile, shutil, urllib2, os, sqlite3
from optparse import OptionParser

script_dir = os.path.abspath(os.path.dirname(__file__))
parser = OptionParser()
parser.add_option("-u", "--url", dest="url", default="http://eve.no-ip.de/inc15/inc15-sqlite3-v1.db.bz2",
                  help="URL from which to download the bz2 compressed database.")
parser.add_option("-f", "--bz-file", dest="bz_file",
                  help="Location of a bz2 archive containing the database "
                       "(if this option is set, download will be skipped)")
parser.add_option("-s", "--sql-script", dest="sql_script", default=os.path.join(script_dir, 'patch_eve_db.sql'),
                  help="Location of the SQL script to apply to the database.")
parser.add_option("-d", "--db-file", dest="db_file", default=os.path.normpath(script_dir + '/../db/EVE.db'),
                  help="Path where to decompress the EVE database file.")


def main(options):
    if not hasattr(options, 'logger'):
        options.logger = logging.getLogger()
        options.logger.addHandler(logging.StreamHandler())
        options.logger.setLevel(logging.INFO)
    log = options.logger
    try:
        f = open(options.sql_script, 'r')
        sql_patch = f.read()
        f.close()

        if options.bz_file is None:
            tempdir = tempfile.mkdtemp()
        
            options.bz_file = os.path.join(tempdir, 'EVE.db.bz2')
            log.info('Downloading EVE original database from %s to %s...', options.url, options.bz_file)
            req = urllib2.urlopen(options.url)
            with open(options.bz_file, 'wb') as fp:
                shutil.copyfileobj(req, fp)
            req.close()
            log.info('Download complete.')
        else:
            tempdir = None
        
        log.info('Expanding %s to %s...', options.bz_file, options.db_file)
        bz_file_desc = bz2.BZ2File(options.bz_file, 'rb')
        with open(options.db_file, 'wb') as db_file_desc:
            shutil.copyfileobj(bz_file_desc, db_file_desc)
        bz_file_desc.close()
        log.info('Expansion complete.')
        
        log.info('Applying SQL patch to EVE database...')
        conn = sqlite3.connect(options.db_file)
        conn.executescript(sql_patch)
        conn.commit()
        conn.close()
        log.info('EVE database successfully patched.')
    finally:
        if tempdir is not None:
            log.info('Removing temp files...')
            shutil.rmtree(tempdir)
            log.info('done')

if __name__ == '__main__':
    options, _ = parser.parse_args()
    main(options)

