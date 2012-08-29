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

__date__ = "2010-02-08"
__author__ = "diabeteman"

import glob
import os
import re
import sys
from optparse import make_option

from django.core.management.base import CommandError, NoArgsCommand
from django.utils.text import get_text_list
from django.utils.jslex import prepare_js_for_gettext

from django.core.management.commands import makemessages


def process_file(file, dirpath, potfile, domain, verbosity, #@ReservedAssignment
                 extensions, wrap, location, stdout=sys.stdout, 
                 extra_keywords=None):
    """
    Extract translatable literals from :param file: for :param domain:
    creating or updating the :param potfile: POT file.

    Uses the xgettext GNU gettext utility.
    """

    from django.utils.translation import templatize

    if verbosity > 1:
        stdout.write('processing file %s in %s\n' % (file, dirpath))
    _, file_ext = os.path.splitext(file)
    if domain == 'djangojs' and file_ext in extensions:
        is_templatized = True
        orig_file = os.path.join(dirpath, file)
        src_data = open(orig_file).read()
        src_data = prepare_js_for_gettext(src_data)
        thefile = '%s.c' % file
        work_file = os.path.join(dirpath, thefile)
        f = open(work_file, "w")
        try:
            f.write(src_data)
        finally:
            f.close()
        
        keywords = ['gettext_noop', 
                    'gettext_lazy', 
                    'ngettext_lazy:1,2',
                    'pgettext:1c,2', 
                    'npgettext:1c,2,3',
                    ]
        if extra_keywords:
            keywords.extend(extra_keywords)
        
        cmd = 'xgettext -d %s -L C %s %s'
        for kw in keywords: 
            cmd += ' --keyword=%s' % kw
        cmd += ' --from-code UTF-8 --add-comments=Translators -o - "%s"'
        cmd %= (domain, wrap, location, work_file)
        
    elif domain == 'django' and (file_ext == '.py' or file_ext in extensions):
        thefile = file
        orig_file = os.path.join(dirpath, file)
        is_templatized = file_ext in extensions
        if is_templatized:
            src_data = open(orig_file, "rU").read()
            thefile = '%s.py' % file
            content = templatize(src_data, orig_file[2:])
            f = open(os.path.join(dirpath, thefile), "w")
            try:
                f.write(content)
            finally:
                f.close()
        work_file = os.path.join(dirpath, thefile)

        keywords = ['gettext_lazy',
                    'ngettext_lazy:1,2',
                    'ugettext_noop',
                    'ugettext_lazy',
                    'ungettext_lazy:1,2',
                    'pgettext:1c,2',
                    'npgettext:1c,2,3',
                    'pgettext_lazy:1c,2',
                    'npgettext_lazy:1c,2,3',
                    ]
        if extra_keywords:
            keywords.extend(extra_keywords)
        
        cmd = 'xgettext -d %s -L Python %s %s'
        for kw in keywords: 
            cmd += ' --keyword=%s' % kw
        cmd += ' --from-code UTF-8 --add-comments=Translators -o - "%s"'
        cmd %= (domain, wrap, location, work_file)
    else:
        return
    msgs, errors = makemessages._popen(cmd)
    if errors:
        if is_templatized:
            os.unlink(work_file)
        if os.path.exists(potfile):
            os.unlink(potfile)
        raise CommandError(
            "errors happened while running xgettext on %s\n%s" %
            (file, errors))
    if msgs:
        makemessages.write_pot_file(potfile, msgs, orig_file, work_file, is_templatized)
    if is_templatized:
        os.unlink(work_file)


def _make_messages(locale=None, domain='django', verbosity=1, all=False, #@ReservedAssignment
        extensions=None, symlinks=False, ignore_patterns=None, no_wrap=False,
        no_location=False, no_obsolete=False, stdout=sys.stdout, 
        extra_keywords=None):
    """
    Uses the ``locale/`` directory from the Django SVN tree or an
    application/project to process all files with translatable literals for
    the :param domain: domain and :param locale: locale.
    """
    # Need to ensure that the i18n framework is enabled
    from django.conf import settings
    if settings.configured:
        settings.USE_I18N = True
    else:
        settings.configure(USE_I18N = True)

    if ignore_patterns is None:
        ignore_patterns = []

    invoked_for_django = False
    if os.path.isdir(os.path.join('conf', 'locale')):
        localedir = os.path.abspath(os.path.join('conf', 'locale'))
        invoked_for_django = True
        # Ignoring all contrib apps
        ignore_patterns += ['contrib/*']
    elif os.path.isdir('locale'):
        localedir = os.path.abspath('locale')
    else:
        raise CommandError("This script should be run from the Django SVN "
                "tree or your project or app tree. If you did indeed run it "
                "from the SVN checkout or your project or application, "
                "maybe you are just missing the conf/locale (in the django "
                "tree) or locale (for project and application) directory? It "
                "is not created automatically, you have to create it by hand "
                "if you want to enable i18n for your project or application.")

    if domain not in ('django', 'djangojs'):
        raise CommandError("currently makemessages only supports domains 'django' and 'djangojs'")

    if (locale is None and not all) or domain is None:
        message = "Type '%s help %s' for usage information." % (os.path.basename(sys.argv[0]), sys.argv[1])
        raise CommandError(message)

    # We require gettext version 0.15 or newer.
    output = makemessages._popen('xgettext --version')[0]
    match = re.search(r'(?P<major>\d+)\.(?P<minor>\d+)', output)
    if match:
        xversion = (int(match.group('major')), int(match.group('minor')))
        if xversion < (0, 15):
            raise CommandError("Django internationalization requires GNU "
                    "gettext 0.15 or newer. You are using version %s, please "
                    "upgrade your gettext toolset." % match.group())

    locales = []
    if locale is not None:
        locales.append(locale)
    elif all:
        locale_dirs = filter(os.path.isdir, glob.glob('%s/*' % localedir))
        locales = [os.path.basename(l) for l in locale_dirs]

    wrap = '--no-wrap' if no_wrap else ''
    location = '--no-location' if no_location else ''

    for locale in locales:
        if verbosity > 0:
            stdout.write("processing language %s\n" % locale)
        basedir = os.path.join(localedir, locale, 'LC_MESSAGES')
        if not os.path.isdir(basedir):
            os.makedirs(basedir)

        pofile = os.path.join(basedir, '%s.po' % domain)
        potfile = os.path.join(basedir, '%s.pot' % domain)

        if os.path.exists(potfile):
            os.unlink(potfile)

        for dirpath, file in makemessages.find_files(".", ignore_patterns, verbosity, #@ReservedAssignment
                stdout, symlinks=symlinks):
            process_file(file, dirpath, potfile, domain, verbosity, extensions,
                    wrap, location, stdout, extra_keywords)

        if os.path.exists(potfile):
            makemessages.write_po_file(pofile, potfile, domain, locale, verbosity, stdout,
                    not invoked_for_django, wrap, location, no_obsolete)




class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--locale', '-l', default=None, dest='locale',
            help='Creates or updates the message files for the given locale (e.g. pt_BR).'),
        make_option('--domain', '-d', default='django', dest='domain',
            help='The domain of the message files (default: "django").'),
        make_option('--all', '-a', action='store_true', dest='all',
            default=False, help='Updates the message files for all existing locales.'),
        make_option('--extension', '-e', dest='extensions',
            help='The file extension(s) to examine (default: "html,txt", or "js" if the domain is "djangojs"). Separate multiple extensions with commas, or use -e multiple times.',
            action='append'),
        make_option('--symlinks', '-s', action='store_true', dest='symlinks',
            default=False, help='Follows symlinks to directories when examining source code and templates for translation strings.'),
        make_option('--ignore', '-i', action='append', dest='ignore_patterns',
            default=[], metavar='PATTERN', help='Ignore files or directories matching this glob-style pattern. Use multiple times to ignore more.'),
        make_option('--no-default-ignore', action='store_false', dest='use_default_ignore_patterns',
            default=True, help="Don't ignore the common glob-style patterns 'CVS', '.*' and '*~'."),
        make_option('--no-wrap', action='store_true', dest='no_wrap',
            default=False, help="Don't break long message lines into several lines"),
        make_option('--no-location', action='store_true', dest='no_location',
            default=False, help="Don't write '#: filename:line' lines"),
        make_option('--no-obsolete', action='store_true', dest='no_obsolete',
            default=False, help="Remove obsolete message strings"),
        make_option('--extra-keyword', dest='extra_keywords',
                    help='If you use import aliases for ugettext and its variations, you can specify it here to make sure that xgettext will find your translatable strings.',
                    action='append')
    )
    help = ("Runs over the entire source tree of the current directory and "
"pulls out all strings marked for translation. It creates (or updates) a message "
"file in the conf/locale (in the django tree) or locale (for projects and "
"applications) directory.\n\nYou must run this command with one of either the "
"--locale or --all options.")

    requires_model_validation = False
    can_import_settings = False

    def handle_noargs(self, *args, **options):
        locale = options.get('locale')
        domain = options.get('domain')
        verbosity = int(options.get('verbosity'))
        process_all = options.get('all')
        extensions = options.get('extensions')
        symlinks = options.get('symlinks')
        ignore_patterns = options.get('ignore_patterns')
        if options.get('use_default_ignore_patterns'):
            ignore_patterns += ['CVS', '.*', '*~']
        ignore_patterns = list(set(ignore_patterns))
        no_wrap = options.get('no_wrap')
        no_location = options.get('no_location')
        no_obsolete = options.get('no_obsolete')
        extra_keywords = options.get('extra_keywords')
        if domain == 'djangojs':
            exts = extensions if extensions else ['js']
        else:
            exts = extensions if extensions else ['html', 'txt']
        extensions = makemessages.handle_extensions(exts)

        if verbosity > 1:
            self.stdout.write('examining files with the extensions: %s\n'
                             % get_text_list(list(extensions), 'and'))

        _make_messages(locale, domain, verbosity, process_all, extensions,
            symlinks, ignore_patterns, no_wrap, no_location, no_obsolete, 
            self.stdout, extra_keywords)

def monkey_patch():
    makemessages.Command = Command
