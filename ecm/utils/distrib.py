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
from ecm import utils
import subprocess
import sys

__date__ = "2010-02-08"
__author__ = "diabeteman"

import os
import setuptools
from distutils.errors import DistutilsArgError


class CompileMessages(setuptools.Command):
    
    description = 'Looks for .po files and compile them to .mo'
    
    # Here we must integrate into distutils "weird" options parser
    # an option definition is a tuple of 3 or 4 elements:
    #    (long_name, short_name, description[, can_be_repeated])
    # note: options that take arguments must have '=' at the end of the long_name
    user_options = [
        ('force', 'f', 
         'Re-generate the files that are already up-to-date'),
        ('base-dir=', 'b',
         'Base directory from where to search .po files (defaults to current dir)'),
        ('msgfmt', 'm',
         'Full path to the msgfmt executable'),
    ]
    boolean_options = ['force']
    
    def initialize_options(self):
        self.force = False
        self.base_dir = None
        self.msgfmt = 'msgfmt'
    
    def finalize_options(self):
        if self.base_dir is not None:
            if not os.path.isdir(self.base_dir):
                raise DistutilsArgError('%s is not a valid directory' % self.base_dir)
        else:
            self.base_dir = '.'
        
        _, ext = os.path.splitext(self.msgfmt)
        if os.name == 'nt' and ext != '.exe':
            self.msgfmt += '.exe'
            
        msgfmt = utils.which(self.msgfmt) 
        if msgfmt is None:
            utils.error('"%s" is not an executable', self.msgfmt)
        else:
            self.msgfmt = msgfmt
    
    def run(self):
        utils.logln('Compiling .po files to .mo binary files...')
        for root, _, files in os.walk(self.base_dir):
            for f in files:
                if f.lower().endswith('.po'):
                    self.process_one_file(root, f)
                    
    
    def process_one_file(self, root, f):
        
        po_file = os.path.normpath(root + '/' + f)
        mo_file = os.path.splitext(po_file)[0] + '.mo'
        
        po_mtime = os.stat(po_file).st_mtime
        if os.path.exists(mo_file):
            mo_mtime = os.stat(mo_file).st_mtime
        else:
            mo_mtime = 0
        
        if not self.force and po_mtime < mo_mtime:
            # files are up to date. Nothing to do
            return
        
        utils.log('Compiling %s... ' % mo_file)
        sys.stdout.flush()
        
        cmd = [self.msgfmt, '--check-format', '-o', mo_file, po_file]
        
        args = []
        for arg in cmd:
            if ' ' in arg:
                args.append('"%s"' % arg)
            else:
                args.append(arg)
        
        try:
            subprocess.check_output(args)
        except subprocess.CalledProcessError, e:
            sys.stdout.write('\n')
            utils.logln(e.output)
            sys.exit(e.returncode)
        
        utils.logln('[ OK ]')
    