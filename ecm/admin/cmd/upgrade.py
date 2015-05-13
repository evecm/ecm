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


__date__ = '2012 3 23'
__author__ = 'diabeteman'

import os
import re
import shutil
import string
from os import path
from distutils import dir_util
from optparse import OptionParser
from ConfigParser import SafeConfigParser

from django.utils.crypto import get_random_string

from ecm.lib.subcommand import Subcommand
from ecm.admin import instance_template
from ecm.admin.util import run_python_cmd, log, pipe_to_django_shell
from ecm.admin.cmd.load import print_load_message
from ecm.admin.cmd import collect_static_files

#-------------------------------------------------------------------------------
def sub_command():
    # UPGRADE
    description = 'Synchronize an instance\'s database and files.'
    upgrade_cmd = Subcommand('upgrade',
                             parser=OptionParser(usage='%prog [OPTIONS] instance_dir'),
                             help=description, callback=run)
    upgrade_cmd.parser.description = description
    upgrade_cmd.parser.add_option('--no-syncdb',
                                  dest='no_syncdb', action='store_true', default=False,
                                  help='Do not modify the instance\'s database.')
    upgrade_cmd.parser.add_option('-u', '--upgrade-from-1.4.9',
                                  dest='upgrade_from_149', action='store_true', default=False,
                                  help='Upgrade from ECM-1.4.9.')
    if not os.name == 'nt':
        upgrade_cmd.parser.add_option('-s', '--symlink-files', dest='symlink_files',
                                      help='Create symbolic links instead of copying static files.',
                                      default=False, action='store_true')

    return upgrade_cmd

#-------------------------------------------------------------------------------
def migrate_ecm_db(instance_dir, upgrade_from_149=False):
    instance_dir = path.abspath(instance_dir)

    log("Migrating database...")
    run_python_cmd('manage.py syncdb --noinput', instance_dir)

    if upgrade_from_149:
        log('Migrating from ECM 1.4.9...')
        # we are upgrading from ECM 1.X.Y, we must perform the init migration
        # on the 'hr' app (rename tables from 'roles_xxxxx' to 'hr_xxxxx')
        pipe_to_django_shell('from south.models import MigrationHistory; '\
                             'MigrationHistory.objects.all().delete()' , instance_dir)

        run_python_cmd('manage.py migrate hr 0001 --noinput', instance_dir)
        # we MUST "fake" the first migration for 1.4.9 apps
        # otherwise the migrate command will fail because DB tables already exist...
        for app in ('common', 'scheduler', 'corp', 'assets', 'accounting'):
            run_python_cmd('manage.py migrate %s 0001 --fake --noinput' % app, instance_dir)

    run_python_cmd('manage.py migrate --all --noinput', instance_dir)

    if upgrade_from_149:
        pipe_to_django_shell('from ecm.apps.scheduler.models import ScheduledTask; '\
                             'ScheduledTask.objects.all().delete()' , instance_dir)
        pipe_to_django_shell('from ecm.apps.common.models import UrlPermission; '\
                             'UrlPermission.objects.all().delete()' , instance_dir)

    log('Database Migration successful.')

#-------------------------------------------------------------------------------
SERVER_NAME_REGEXP = re.compile('ServerName (.+)', re.IGNORECASE)
def upgrade_instance_files(instance_dir, config):
    log('Upgrading instance config files & examples...')

    apache_mod_wsgi_vhost = path.join(instance_dir, 'examples/apache_mod_wsgi_vhost.example')
    apache_proxy_vhost = path.join(instance_dir, 'examples/apache_reverse_proxy.example')
    try:
        with open(apache_proxy_vhost) as fd:
            buff = fd.read()
        match = SERVER_NAME_REGEXP.search(buff)
        if match:
            host_name = match.group(1)
        else:
            host_name = '???'
    except IOError:
        buff = ''
        host_name = '???'

    template_dir = path.abspath(path.dirname(instance_template.__file__))
    shutil.copy(path.join(template_dir, 'settings.py'), instance_dir)
    shutil.copy(path.join(template_dir, 'manage.py'), instance_dir)
    dir_util.copy_tree(path.join(template_dir, 'wsgi'), path.join(instance_dir, 'wsgi'))
    dir_util.copy_tree(path.join(template_dir, 'examples'), path.join(instance_dir, 'examples'))
    if hasattr(os, 'chmod'):
        os.chmod(path.join(instance_dir, 'manage.py'), 00755)

    options = {
        'host_name': host_name,
        'instance_dir': path.abspath(instance_dir),
        'bind_address': config.get('misc', 'server_bind_ip'),
        'bind_port': config.get('misc', 'server_bind_port'),
    }

    try:
        with open(apache_mod_wsgi_vhost, 'r') as fd:
            buff = fd.read()
        buff = buff % options
        with open(apache_mod_wsgi_vhost, 'w') as fd:
            buff = fd.write(buff)
    except IOError, err:
        log(err)
    try:
        with open(apache_proxy_vhost, 'r') as fd:
            buff = fd.read()
        buff = buff % options
        with open(apache_proxy_vhost, 'w') as fd:
            buff = fd.write(buff)
    except IOError, err:
        log(err)

    if not config.has_option('misc', 'secret_key'):
        # Create a random SECRET_KEY hash to put it in the main settings.
        chars = string.ascii_letters + string.digits + '.,;:!@#$^&*(-_+)[]{}'
        config.set('misc', 'secret_key', get_random_string(50, chars))

    template_dir = path.abspath(path.dirname(instance_template.__file__))
    default_config = SafeConfigParser()
    default_config.read([path.join(template_dir, 'settings.ini')])

    for section in default_config.sections():
        for option in default_config.options(section):
            if not config.has_option(section, option):
                config.set(section, option, default_config.get(section, option))

    settings_fd = open(path.join(instance_dir, 'settings.ini'), 'w')
    config.write(settings_fd)
    settings_fd.close()

#-------------------------------------------------------------------------------
def run(command, global_options, options, args):
    if not args:
        command.parser.error('Missing instance directory.')
    instance_dir = args[0]
    config = SafeConfigParser()
    config.read([path.join(instance_dir, 'settings.ini')])
    
    # upgrade files from template
    upgrade_instance_files(instance_dir, config)

    # run collectstatic
    collect_static_files(instance_dir, options)

    # migrate ecm db
    if not options.no_syncdb:
        migrate_ecm_db(instance_dir, options.upgrade_from_149)

    log('')
    log('ECM instance upgraded in "%s".' % instance_dir)

    print_load_message(instance_dir, config.get('database', 'ecm_engine'))
