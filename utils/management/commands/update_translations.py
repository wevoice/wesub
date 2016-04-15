"""
update_translations -- Update our gettext translation files

This command does basically the same thing as Django's makemessages command.
The reason that we implement our own is the standard one runs really slow.  My
(BDK) best guess is that it's because it tries to process too many files and
there's no good way to change the behavoir on our current django version.

Here's our basic strategy:
  - We create 2 gettext domains -- "django" for python/template strings and
    "djangojs" for javascript strings.

  - For each domain, we create a .po template file (.pot file for short).
    This stores all translatable strings in the app for that domain.

  - For each locale/domain pair we create a .po file which is basically a copy
    of the .pot file with localized strings filled in in that language.  To do
    this we merge the new .pot file with the existing .po file.

  - Outside of this command we use the transifex client to pull in new
    localized strings and update the .po files.

One tricky part is the template files.  gettext can't handle these natively,
we need to run them through Django's templatize() function.  To allow gettext
to see the output, we create a temporary directory and store the output of
templatize() for each template in a path relative to the temp directory.
"""

import glob
import os
import shutil
import subprocess
import tempfile

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.translation import templatize

import optionalapps

def locale_dir():
    return os.path.join(settings.PROJECT_ROOT, 'locale')

def check_xgettext_call(*args, **kwargs):
    """Run subprocess.check_call for xgettext.

    These commands tend to have really long command lines, so we shorten the
    error message if they fail.
    """
    try:
        subprocess.check_call(*args, **kwargs)
    except subprocess.CalledProcessError, e:
        e.cmd = 'xgettext'
        raise e

class TranslationDomain(object):
    """
    Base class for translation domains.

    Subclasses of this are responsible for running gettext to build the .pot
    file for their domain
    """

    # Name of the domain
    name = NotImplemented

    def pot_path(self):
        return os.path.join(locale_dir(), '{}.pot'.format(self.name))

    def po_path(self, locale_name):
        return os.path.join(locale_dir(), locale_name, 'LC_MESSAGES',
                            '{}.po'.format(self.name))

    def build_pot_file(self):
        """Build the .pot file for this domain
        """
        raise NotImplementedError()

    def find_files(self, root_dirpath, extension=None):
        for dirpath, dirnames, filenames in os.walk(root_dirpath):
            for skip_dir in self.DIRS_TO_SKIP:
                if skip_dir in dirnames:
                    dirnames.remove(skip_dir)
            for filename in filenames:
                if extension is None or filename.endswith(extension):
                    yield os.path.relpath(os.path.join(dirpath, filename),
                                          settings.PROJECT_ROOT)

class DjangoTranslationDomain(TranslationDomain):
    name = 'django'

    DIRS_TO_SKIP = [
        'migrations',
        'management',
        'tests',
    ]

    def build_pot_file(self):
        self.tempdir = tempfile.mkdtemp(prefix='amara-templates')
        try:
            cmdline = [
                'xgettext',
                '-d', 'django', '-L', 'Python',
                '-D', self.tempdir, '-D', settings.PROJECT_ROOT,
                '--from-code=UTF-8',
                '-o', self.pot_path(),
            ]
            cmdline.extend(self.find_python_files())
            cmdline.extend(self.find_and_copy_template_files())
            check_xgettext_call(cmdline)
        finally:
            shutil.rmtree(self.tempdir)

    def find_python_files(self):
        dirs_to_search = []
        dirs_to_search.append(os.path.join(settings.PROJECT_ROOT, 'apps'))
        dirs_to_search.extend(optionalapps.get_repository_paths())

        for dir_path in dirs_to_search:
            for path in self.find_files(dir_path, '.py'):
                yield path

    def find_template_dirs(self):
        yield os.path.join(settings.PROJECT_ROOT, 'templates')
        globspec = os.path.join(settings.PROJECT_ROOT, 'apps', '*', 'templates')
        for path in glob.glob(globspec):
            if os.path.isdir(path):
                yield path

        for app_name in optionalapps.get_apps():
            mod = __import__(app_name)
            app_template_dir = os.path.join(os.path.dirname(mod.__file__),
                                            'templates')
            if os.path.isdir(app_template_dir):
                yield app_template_dir

    def find_and_copy_template_files(self):
        for dir_path in self.find_template_dirs():
            for path in self.find_files(dir_path):
                self.copy_template_file(path)
                yield path

    def copy_template_file(self, path):
        path = os.path.relpath(path, settings.PROJECT_ROOT)
        dest_path = os.path.join(self.tempdir, path)
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        with open(dest_path, 'w') as f_out:
            with open(path, 'r') as f_in:
                f_out.write(templatize(f_in.read()))

class DjangoJSTranslationDomain(TranslationDomain):
    name = 'djangojs'
    # TODO: implement this

class Locale(object):
    """
    Manage a single translation locale

    We create a locale for each language that we want to translate to.  For
    each domain, the locale stores a .po file which contains translated
    strings and a .mo file which is a compiled version of the .po file.
    """
    def __init__(self, name):
        self.name = name

    def directory(self):
        return os.path.join(locale_dir(), self.name)

    def merge_pot_file(self, domain):
        subprocess.check_call([
            'msgmerge', '--previous', '-q',
            '-o', domain.po_path(self.name),
            domain.po_path(self.name),
            domain.pot_path(),
        ])
        self.remove_obsolete_messages(domain)

    def remove_obsolete_messages(self, domain):
        subprocess.check_call([
            'msgattrib', '--no-obsolete',
            '-o', domain.po_path(self.name),
            domain.po_path(self.name),
        ])

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        os.chdir(settings.PROJECT_ROOT)

        self.domains = [
            DjangoTranslationDomain(),
            #DjangoJSTranslationDomain(),
        ]

        for domain in self.domains:
            self.stdout.write("building {}\n".format(domain.pot_path()))
            domain.build_pot_file()

        for domin in self.domains:
            for locale in self.all_locales():
                self.stdout.write(
                    "building {}\n".format(domain.po_path(locale.name)))
                locale.merge_pot_file(domain)

    def all_locales(self):
        for name in os.listdir(locale_dir()):
            if os.path.isdir(os.path.join(locale_dir(), name)):
                yield Locale(name)
