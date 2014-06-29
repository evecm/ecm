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

__date__ = '2012 3 25'
__author__ = 'diabeteman'

import os
import sys
import signal
import shutil
import subprocess
from subprocess import PIPE

from django.core.management.color import supports_color
from django.utils.termcolors import colorize

#-------------------------------------------------------------------------------
def prompt(message, default_value=None, valid_list=None):
    value = None

    if valid_list is not None:
        list_str = '{%s}' % '|'.join(map(str, valid_list))
        message = '%s %s' % (message, list_str)

    if default_value is not None:
        message = '%s [default=%s]' % (message, default_value)

    if supports_color():
        message = colorize('[ECM] ', fg='cyan', opts=('bold',)) + colorize(message, fg='magenta') + ' '
    else:
        message = '[ECM] ' + message + ' '

    if valid_list is not None:
        while value not in valid_list:
            value = raw_input(message)
            if not value:
                value = default_value
    else:
        while not value:
            value = raw_input(message)
            if not value:
                value = default_value

    return value

#-------------------------------------------------------------------------------
def expand(archive_file, target_dir):
    
    base, extension = os.path.splitext(archive_file)
    output_file = os.path.join(target_dir, os.path.basename(base))
    
    if extension == '.bz2':
        import bz2
        output_file = os.path.join(target_dir, os.path.basename(base))
        source = bz2.BZ2File(archive_file, 'rb')
        target = open(output_file, 'wb')
        shutil.copyfileobj(source, target)
        source.close()
        target.close()
    
    elif extension == '.gz':
        import gzip
        output_file = os.path.join(target_dir, os.path.basename(base))
        source = gzip.GzipFile(archive_file, 'rb')
        target = open(output_file, 'wb')
        shutil.copyfileobj(source, target)
        source.close()
        target.close()
        
    elif extension == '.zip':
        import zipfile
        zip_file = zipfile.ZipFile(archive_file, 'r')
        source = zip_file.open(zip_file.namelist()[0]) # take first name from zip file
        target = open(output_file, 'wb')
        shutil.copyfileobj(source, target)
        source.close()
        target.close()
    else:
        raise NotImplementedError('Unsupported archive format "%s"' % archive_file)
    
    return output_file


#-------------------------------------------------------------------------------
def run_python_cmd(command_line, run_dir, exit_on_failure=True):
    if isinstance(command_line, basestring):
        command_line = command_line.strip().split()

    command_line.insert(0, sys.executable)

    run_command(command_line, run_dir)

#-------------------------------------------------------------------------------
def run_command(command_line, run_dir, exit_on_failure=True, **kwargs):
    if isinstance(command_line, basestring):
        command_line = command_line.strip().split()

    log('$ ' + ' '.join(command_line))
    proc = None
    try:
        proc = subprocess.Popen(command_line, cwd=run_dir, universal_newlines=True, **kwargs)
        exitcode = proc.wait()
        if exitcode != 0 and exit_on_failure:
            sys.exit(exitcode)
    except KeyboardInterrupt:
        if proc is not None:
            os.kill(proc.pid, signal.SIGTERM)


#-------------------------------------------------------------------------------
def pipe_to_django_shell(python_code, run_dir, exit_on_failure=True):
    
    log('Piping code to django shell: %r' % python_code)
    
    command_line = [sys.executable, 'manage.py', 'shell']
    proc = None
    try:
        proc = subprocess.Popen(command_line, stdin=PIPE, stdout=PIPE, stderr=PIPE, 
                                cwd=run_dir, universal_newlines=True)
        (_, stderr) = proc.communicate(python_code)
        exitcode = proc.wait()
        if (exitcode != 0 or stderr) and exit_on_failure:
            print >>sys.stderr, stderr
            sys.exit(exitcode)
    except KeyboardInterrupt:
        if proc is not None:
            os.kill(proc.pid, signal.SIGTERM)

#-------------------------------------------------------------------------------
def pipe_to_dbshell(sql_file, run_dir, password=None, exit_on_failure=True):
    
    command_line = [sys.executable, 'manage.py', 'dbshell']
    proc = None
    try:
        if password is not None:
            # workaround for postgres, 
            # cannot pass password through command line options
            os.environ['PGPASSWORD'] = password
        
        proc = subprocess.Popen(command_line, stdin=PIPE, stdout=PIPE, stderr=PIPE, 
                                cwd=run_dir, universal_newlines=True, bufsize=-1)
        
        if os.path.exists(sql_file):
            sql_fd = open(sql_file, 'rb')
            # Pass data in blocks to avoid huge memory usage when importing sql
            blocksize = 1000000
            sql = sql_fd.read(blocksize)
            while(len(sql)):
                proc.stdin.write(sql)
                sql = sql_fd.read(blocksize)
            
            sql_fd.close()
        else:
            sql = sql_file
        
        stdout, stderr = proc.communicate(sql)
            
        exitcode = proc.wait()
        if exitcode != 0 and exit_on_failure:
            print >>sys.stderr, stderr
            sys.exit(exitcode)
        
        return stdout
    
    except KeyboardInterrupt:
        if proc is not None:
            os.kill(proc.pid, signal.SIGTERM)

#-------------------------------------------------------------------------------
def log(message, *args):
    message = message % args
    if supports_color():
        print colorize('[ECM] ', fg='cyan', opts=('bold',)) +  message
    else:
        print '[ECM] ' + message

