#!/usr/bin/env python
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
import sys




__date__ = "2010-01-24"
__author__ = "diabeteman"

import shutil
from distutils import dir_util
import os
from os import path
import tarfile
import tempfile
from optparse import OptionValueError

import functions
import config


#-------------------------------------------------------------------------------
def install(options):
    log = functions.get_logger()

    log.info("Installing ECM server version %s...", options.version)

    if options.db_engine is not None:
        if options.db_engine not in config.DB_ENGINES.keys():
            raise OptionValueError("DB engine must be one of %s." % config.DB_ENGINES.keys())
    else:
        options.db_engine = functions.prompt('DB engine?', config.DB_ENGINES.keys())
    options.db_engine = config.DB_ENGINES[options.db_engine]

    if options.vhost_name is None:
        options.vhost_name = functions.prompt("Apache virtual host name? (example: ecm.mydomain.com)")

    if options.admin_email is None:
        options.admin_email = functions.prompt("Email of the server administrator? (for error notifications)")

    if options.server_email is None:
        domain = options.vhost_name.split('.', 1)
        options.server_email = 'ecm.admin@%s' % domain[-1]
    if not options.quiet:
        raw_input("If the installation directory already exists, it will be deleted. "
                  "Press 'enter' to proceed with the installation.")
    functions.install_files(options)
    functions.download_eve_db(options)
    functions.configure_apache(options)
    functions.configure_ecm(options)
    functions.restore_permissions(options)
    functions.init_ecm_db(options)

    vhost_file = os.path.join(options.install_dir, "ecm.apache.vhost.conf")
    settings_file = os.path.join(options.install_dir, "ecm/settings.py")
    log.info("")
    log.info("INSTALLATION SUCCESSFUL")
    log.info("")
    log.info("Apache virtual host file '%s' generated. Please include it to your apache configuration.", path.normpath(vhost_file))
    log.info("")
    log.info("Note: if needed, you can edit '%s' to change database and email settings.", path.normpath(settings_file))

#-------------------------------------------------------------------------------
def upgrade(options):

    log = functions.get_logger()

    log.info("Upgrading ECM server to version %s...", options.version)

    tempdir = tempfile.mkdtemp()
    file_stat = functions.backup_settings(options, tempdir)

    if not options.quiet:
        raw_input("Press 'enter' to proceed with the migration.")

    functions.install_files(options)
    dir_util.copy_tree(tempdir, options.install_dir)
    functions.configure_apache(options)
    functions.configure_ecm(options)
    if options.quiet or functions.prompt("Upgrade EVE database?") in ['y', 'yes', 'Y']:
        functions.download_eve_db(options)
    functions.restore_permissions(options, file_stat)

    log.info("Deleting temp dir %s...", tempdir)
    dir_util.remove_tree(tempdir)

    functions.migrate_ecm_db(options)

    log.info("")
    log.info("UPGRADE SUCCESSFUL")



#-------------------------------------------------------------------------------
def package(options):
    package_dir = tempfile.mkdtemp()
    try:
        package_src_dir =  os.path.join(package_dir, "src")
        print "Copying files to package dir..."
        shutil.copytree(src=options.src_dir, dst=package_src_dir, ignore=functions.ignore_func)
        root_dir = path.abspath(path.dirname(__file__))
        shutil.copy(path.join(root_dir, 'functions.py'), package_dir)
        shutil.copy(path.join(root_dir, 'config.py'), package_dir)
        shutil.copy(path.join(root_dir, 'setup.py'), package_dir)
        shutil.copy(path.join(root_dir, 'LICENSE'), package_dir)
        shutil.copy(path.join(root_dir, 'README'), package_dir)
        print "Inserting timestamp in __init__.py file..."
        init_file = os.path.join(os.path.join(package_src_dir, "ecm/__init__.py"))
        options.timestamp = functions.set_timestamp(init_file)
        print "Version %s.%s" % (options.version, options.timestamp)

        print "Creating archive..."
        if os.path.exists(options.dist_dir):
            dir_util.remove_tree(options.dist_dir)
        dir_util.mkpath(options.dist_dir)
        archive_name = os.path.normpath("ECM-%s.tar.gz" % options.version)

        curdir = os.getcwd()
        os.chdir(options.dist_dir)
        tar = tarfile.open(archive_name, "w:gz")
        tar.add(package_dir, arcname="ECM-%s" % options.version)
        tar.close()
        os.chdir(curdir)
        print "Archive generated: %s" % path.join(options.dist_dir, archive_name)
    finally:
        print "Deleting package dir..."
        dir_util.remove_tree(package_dir)


#-------------------------------------------------------------------------------
if __name__ == '__main__':
    root_dir = path.abspath(path.dirname(__file__))
    version, timestamp = functions.get_timestamp(root_dir)
    cmd, options = config.parse_args(version, timestamp)

    try:
        if cmd == 'install':
            install(options)
        elif cmd == 'package':
            package(options)
        elif cmd == 'upgrade':
            upgrade(options)
    except:
        functions.get_logger().exception('')
        sys.exit(1)
