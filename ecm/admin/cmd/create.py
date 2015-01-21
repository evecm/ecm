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

__date__ = '2015 1 21'
__author__ = 'diabeteman'

import os
from os import path
import shutil
import string
from ConfigParser import SafeConfigParser
from optparse import OptionParser, OptionGroup

from django.utils.crypto import get_random_string

from ecm.admin import instance_template
from ecm.admin.util import prompt, log
from ecm.lib.subcommand import Subcommand

DB_ENGINES = {
    'postgresql': 'django.db.backends.postgresql_psycopg2',
    'mysql': 'django.db.backends.mysql',
    'sqlite': 'django.db.backends.sqlite3',
    'oracle': 'django.db.backends.oracle'
}

#------------------------------------------------------------------------------
def sub_command():
    # CREATE
    description = 'Create a new ECM instance in the given directory.'
    
    create_cmd = Subcommand('create',
                            parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                            help='Create a new ECM instance in the given directory.',
                            callback=run)
    create_cmd.parser.description = description
    create_cmd.parser.add_option('-q', '--quiet', dest='quiet',
                                 help='Do not prompt user (use default values).',
                                 default=False, action='store_true')

    db_group = OptionGroup(create_cmd.parser, 'Database options')
    db_group.add_option('--db-engine', dest='db_engine',
                        help='DB engine %s' % DB_ENGINES.keys())
    db_group.add_option('--db-host', dest='db_host',
                        help='Database host')
    db_group.add_option('--db-name', dest='db_name',
                        help='Database name')
    db_group.add_option('--db-user', dest='db_user',
                        help='Database user')
    db_group.add_option('--db-password', dest='db_pass',
                        help='Database user password')
    create_cmd.parser.add_option_group(db_group)

    w_group = OptionGroup(create_cmd.parser, 'Web & Mail options')
    w_group.add_option('--host-name', dest='host_name',
                       help='The public name of ECM host computer.')
    w_group.add_option('--admin-email', dest='admin_email',
                       help='Email of the server administrator (for error notifications)')
    w_group.add_option('--server-email', dest='server_email',
                       help='Email used as "from" address in emails sent by the server.')
    create_cmd.parser.add_option_group(w_group)

    server_group = OptionGroup(create_cmd.parser, 'Server options')
    server_group.add_option('--bind-address', dest='bind_address',
                            help='Server listening address')
    server_group.add_option('--bind-port', dest='bind_port',
                            help='Server listening address')
    create_cmd.parser.add_option_group(server_group)

    return create_cmd


#------------------------------------------------------------------------------
def init_instance(command, args):
    """
    Create the instance directory and copy the template scripts in it.
    """
    if not args:
        command.parser.error('Missing instance directory.')
    instance_dir = args[0]
    if path.exists(instance_dir):
        command.parser.error('Directory "%s" already exists.' % instance_dir)
    try:
        # check if the instance dir is not named like an existing package
        instance_dir_name = path.basename(instance_dir)
        __import__(instance_dir_name)
        command.parser.error('Cannot create an instance in a folder named "%s".' % instance_dir_name
                             + ' It clashes with another python package.' )
    except ImportError:
        pass
    template_dir = path.abspath(path.dirname(instance_template.__file__))
    shutil.copytree(template_dir, instance_dir)
    
    if hasattr(os, 'chmod'):
        os.chmod(path.join(instance_dir, 'manage.py'), 00755)

    return instance_dir

#------------------------------------------------------------------------------
def prompt_missing_options(options):
    """
    Prompt the user if necessary.
    """
    if not options.db_engine:
        options.db_engine = prompt('Database engine?', default_value='sqlite', valid_list=DB_ENGINES.keys())
        options.db_engine = DB_ENGINES.get(options.db_engine, options.db_engine)
    if options.db_engine != DB_ENGINES['sqlite']:
        if not options.db_host:
            options.db_host = prompt('Database host?', default_value='localhost')
        if not options.db_name:
            options.db_name = prompt('Database name?', default_value='ecm')
        if not options.db_user:
            options.db_user = prompt('Database user?', default_value='ecm')
        if not options.db_pass:
            options.db_pass = prompt('Database password?', default_value='ecm')
    if not options.host_name:
        options.host_name = prompt('External host name?')
    if not options.admin_email:
        options.admin_email = prompt('Email of the server administrator? (for error notifications)')
    if not options.server_email:
        options.server_email = prompt('Email used as "from" address in emails sent by the server?')
    if not options.bind_address:
        options.bind_address = prompt('Embedded server listening address?', default_value='127.0.0.1')
    if not options.bind_port:
        options.bind_port = prompt('Embedded server listening port?', default_value=8888)

#------------------------------------------------------------------------------
def write_settings(command, options, instance_dir):
    """
    Write all options/settings to the settings.ini file.
    """
    config = SafeConfigParser()
    settings_file = path.normpath(path.join(instance_dir, 'settings.ini'))
    if not config.read(settings_file):
        raise IOError('Could not read %s' % settings_file)
    config.set('misc', 'debug', 'False')
    config.set('misc', 'server_bind_ip', str(options.bind_address))
    config.set('misc', 'server_bind_port', str(options.bind_port))
    config.set('misc', 'pid_file', 'ecm.pid')
    config.set('misc', 'external_host_name', str(options.host_name))
    config.set('database', 'ecm_engine', str(options.db_engine))
    if options.db_name:
        config.set('database', 'ecm_host', str(options.db_host))
        config.set('database', 'ecm_name', str(options.db_name))
        config.set('database', 'ecm_user', str(options.db_user))
        config.set('database', 'ecm_password', str(options.db_pass))
    config.set('email', 'admin_email', str(options.admin_email))
    config.set('email', 'default_from_email', str(options.server_email))
    config.set('email', 'server_email', str(options.server_email))
    
    # Create a random SECRET_KEY hash to put it in the main settings.
    chars = string.ascii_letters + string.digits + '.,;:!@#$^&*(-_+)[]{}'
    config.set('misc', 'secret_key', get_random_string(50, chars))
    
    settings_fd = open(settings_file, 'w')
    config.write(settings_fd)
    settings_fd.close()

    instance_dir = path.abspath(instance_dir)
    apache_mod_wsgi_vhost = path.join(instance_dir, 'examples/apache_mod_wsgi_vhost.example')
    apache_proxy_vhost = path.join(instance_dir, 'examples/apache_reverse_proxy.example')
    options.instance_dir = instance_dir

    with open(apache_mod_wsgi_vhost, 'r') as fd:
        buff = fd.read()
    buff = buff % options.__dict__
    with open(apache_mod_wsgi_vhost, 'w') as fd:
        buff = fd.write(buff)

    with open(apache_proxy_vhost, 'r') as fd:
        buff = fd.read()
    buff = buff % options.__dict__
    with open(apache_proxy_vhost, 'w') as fd:
        buff = fd.write(buff)


#------------------------------------------------------------------------------
def run(command, global_options, options, args):
    """
    Create a new ECM instance.
    """
    instance_dir = init_instance(command, args)
    if options.quiet:
        return
    try:
        prompt_missing_options(options)
        write_settings(command, options, instance_dir)
        log('')
        log('New ECM instance created in "%s".' % instance_dir)
        log('Please check the configuration in "%s" before running `ecm-admin init "%s"`.'
                 % (path.join(instance_dir, 'settings.ini'), instance_dir))
    except:
        # delete the created instance directory if something goes wrong
        shutil.rmtree(instance_dir, ignore_errors=True)
        raise
