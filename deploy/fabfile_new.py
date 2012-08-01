# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.
from __future__ import with_statement

import os, sys, string, random
from datetime import datetime
from functools import wraps
import time

import fabric.colors as colors
from fabric.api import run, sudo, env, cd, local as _local, abort, task
from fabric.context_managers import settings, hide
from fabric.utils import fastprint
from fabric.decorators import roles, runs_once, parallel

ADD_TIMESTAMPS = """ | awk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $0; fflush(); }' """
WRITE_LOG = """ | tee /tmp/%s.log """

# Output Management -----------------------------------------------------------
PASS_THROUGH = ('sudo password: ', 'Sorry, try again.')
class CustomFile(file):
    def __init__(self, *args, **kwargs):
        self.log = ""
        return super(CustomFile, self).__init__(*args, **kwargs)

    def _record(self, s):
        self.log = self.log[-255:] + s.lower()

        if any(pt in self.log for pt in PASS_THROUGH):
            sys.__stdout__.write('\n\n' + self.log.rsplit('\n', 1)[-1])
            self.log = ""

    def write(self, s, *args, **kwargs):
        self._record(s)
        return super(CustomFile, self).write(s, *args, **kwargs)


_out_log = CustomFile('fabric.log', 'w')
class Output(object):
    """A context manager for wrapping up standard output/error nicely.

    Basic usage:

        with Output("Performing task foo"):
            ...

    This will print a nice header, redirect all output (except for password
    prompts) to a log file, and then unredirect the output when it's finished.

    If you need to override the redirection inside the body, you can use the
    fastprint and fastprintln methods on the manager:

        with Output("Performing task foo") as out:
            ...
            if something:
                out.fastprintln('Warning: the disk is getting close to full.')
            ...

    WARNING: Do not nest 'with Output(...)' blocks!  I have no idea how that
    will behave at the moment.  This includes calling a function that contains
    an Output block from within an Output block.

    TODO: Fix this.

    """
    def __init__(self, message=""):
        self.message = message

    def __enter__(self):
        if self.message:
            fastprint(colors.white(self.message.ljust(60) + " -> ", bold=True))

        sys.stdout = _out_log
        sys.stderr = _out_log

        if self.message:
            fastprint("\n\n")
            fastprint(colors.yellow("+" + "-" * 78 + "+\n", bold=True))
            fastprint(colors.yellow("| " + self.message.ljust(76) + " |\n", bold=True))
            fastprint(colors.yellow("+" + "-" * 78 + "+\n", bold=True))

        return self

    def __exit__(self, type, value, tb):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if type is None:
            fastprint(colors.green("OK\n", bold=True))
        else:
            fastprint(colors.red("FAILED\n", bold=True))
            fastprint(colors.red(
                "\nThere was an error.  "
                "See ./fabric.log for the full transcript of this run.\n",
                bold=True))

    def fastprint(self, s):
        sys.stdout = sys.__stdout__
        fastprint(s)
        sys.stdout = _out_log

    def fastprintln(self, s):
        self.fastprint(s + '\n')

def _lock(*args, **kwargs):
    """
    Creates a temporary "lock" file to prevent concurrent deployments

    """
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        res = run('cat {0}'.format(env.deploy_lock))
    if res.succeeded:
        abort('Another operation is currently in progress: {0}'.format(res))
    else:
        task = kwargs.get('task', '')
        with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
            run('echo "{0} : {1}" > {2} {3}'.format(datetime.now(), env.user, env.deploy_lock, task))

def _unlock(*args, **kwargs):
    """
    Removes deploy lock

    """
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        run('rm -f {0}'.format(env.deploy_lock))

def lock_required(f):
    """
    Decorator for the lock / unlock functionality

    """
    @wraps(f)
    def decorated(*args, **kwargs):
        _lock()
        out = None
        try:
            out = f(*args, **kwargs)
        except:
            pass
        finally:
            _unlock()
        return out
    return decorated

@task
def remove_lock():
    """
    Removes lock from hosts (in the event of a failed task)

    """
    with Output('Removing lock'):
        _execute_on_all_hosts(lambda dir: _unlock(dir))

def _local(*args, **kwargs):
    '''Override Fabric's local() to facilitate output logging.'''
    capture = kwargs.get('capture')

    kwargs['capture'] = True
    out = _local(*args, **kwargs)

    if capture:
        return out
    else:
        print out

def _create_env(username,
                name,
                s3_bucket,
                app_name,
                app_dir,
                app_group,
                revision,
                ve_dir,
                separate_uslogging_db,
                key_filename,
                roledefs={}):
    env.user = username
    env.installation_name = name
    env.s3_bucket = s3_bucket
    env.app_name = app_name
    env.app_dir = app_dir
    env.app_group = app_group
    env.revision = revision
    env.ve_dir = ve_dir
    env.separate_uslogging_db = separate_uslogging_db
    env.key_filename = key_filename
    env.roledefs = roledefs
    env.deploy_lock = '/tmp/.amara_deploy_{0}'.format(revision)

@task
def local():
    """
    Configure task(s) to run in the local environment

    """
    with Output("Configuring task(s) to run on LOCAL"):
        _create_env(username              = 'vagrant',
                    name                  = 'local',
                    s3_bucket             = 's3.staging.universalsubtitles.org',
                    app_name              = 'unisubs',
                    app_dir               = '/opt/apps/local/unisubs/',
                    app_group             = 'deploy',
                    revision              = 'staging',
                    ve_dir                = '/opt/ve/local/unisubs',
                    separate_uslogging_db = False,
                    key_filename          = "~/.vagrant.d/insecure_private_key",
                    roledefs              = {
                        'app': ['10.10.10.115'],
                        'data': ['10.10.10.120'],
                    },)

# def staging(username):
#     with Output("Configuring task(s) to run on STAGING"):
#         _create_env(username              = username,
#                     hosts                 = ['pcf-us-staging3.pculture.org:2191',
#                                             'pcf-us-staging4.pculture.org:2191'],
#                     hostnames_squid_cache = ['staging.universalsubtitles.org',
#                                              'staging.amara.org'
#                                              ],
#                     s3_bucket             = 's3.staging.universalsubtitles.org',
#                     installation_dir      = 'universalsubtitles.staging',
#                     static_dir            = '/var/static/staging',
#                     name                  = 'staging',
#                     git_branch            = 'staging',
#                     memcached_bounce_cmd  = '/etc/init.d/memcached restart',
#                     admin_dir             = '/usr/local/universalsubtitles.staging',
#                     admin_host            = 'pcf-us-adminstg.pculture.org:2191',
#                     celeryd_host          = 'pcf-us-adminstg.pculture.org:2191',
#                     celeryd_proj_root     = 'universalsubtitles.staging',
#                     separate_uslogging_db = True,
#                     celeryd_start_cmd     = "/etc/init.d/celeryd start",
#                     celeryd_stop_cmd      = "/etc/init.d/celeryd stop",
#                     celeryd_bounce_cmd    = "/etc/init.d/celeryd restart &&  /etc/init.d/celeryevcam start")
#
# def dev(username):
#     with Output("Configuring task(s) to run on DEV"):
#         _create_env(username              = username,
#                     hosts                 = ['dev.universalsubtitles.org:2191'],
#                     hostnames_squid_cache = ['dev.universalsubtitles.org',
#                                              'dev.amara.org'
#                                              ],
#                     s3_bucket             = None,
#                     installation_dir      = 'universalsubtitles.dev',
#                     static_dir            = '/var/www/universalsubtitles.dev',
#                     name                  = 'dev',
#                     git_branch            = 'dev',
#                     memcached_bounce_cmd  = '/etc/init.d/memcached restart',
#                     admin_dir             = None,
#                     admin_host            = 'dev.universalsubtitles.org:2191',
#                     celeryd_host          = DEV_HOST,
#                     celeryd_proj_root     = 'universalsubtitles.dev',
#                     separate_uslogging_db = False,
#                     celeryd_start_cmd     = "/etc/init.d/celeryd.dev start",
#                     celeryd_stop_cmd      = "/etc/init.d/celeryd.dev stop",
#                     celeryd_bounce_cmd    = "/etc/init.d/celeryd.dev restart &&  /etc/init.d/celeryevcam.dev start")
#
# def production(username):
#     with Output("Configuring task(s) to run on PRODUCTION"):
#         _create_env(username              = username,
#                     hosts                 = ['pcf-us-cluster3.pculture.org:2191',
#                                              'pcf-us-cluster4.pculture.org:2191',
#                                              'pcf-us-cluster5.pculture.org:2191',
#                                              'pcf-us-cluster8.pculture.org:2191',
#                                              'pcf-us-cluster9.pculture.org:2191',
#                                              'pcf-us-cluster10.pculture.org:2191',
#                                              ],
#                     hostnames_squid_cache = ['www.universalsubtitles.org',
#                                              'www.amara.org',
#                                              'universalsubtitles.org',
#                                              'amara.org'
#                                              ],
#                     s3_bucket             = 's3.www.universalsubtitles.org',
#                     installation_dir      = 'universalsubtitles',
#                     static_dir            = '/var/static/production',
#                     name                  =  None,
#                     git_branch            = 'production',
#                     memcached_bounce_cmd  = '/etc/init.d/memcached restart',
#                     admin_dir             = '/usr/local/universalsubtitles',
#                     admin_host            = 'pcf-us-admin.pculture.org:2191',
#                     celeryd_host          = 'pcf-us-admin.pculture.org:2191',
#                     celeryd_proj_root     = 'universalsubtitles',
#                     separate_uslogging_db = True,
#                     celeryd_start_cmd     = "/etc/init.d/celeryd start",
#                     celeryd_stop_cmd      = "/etc/init.d/celeryd stop",
#                     celeryd_bounce_cmd    = "/etc/init.d/celeryd restart  && /etc/init.d/celeryevcam start ")
#
# def temp(username):
#     with Output("Configuring task(s) to run on TEMP"):
#         _create_env(username              = username,
#                     hosts                 = ['pcf-us-tmp1.pculture.org:2191',],
#                     hostnames_squid_cache = ['tmp.universalsubtitles.org',
#                                              'tmp.amara.org'
#                                              ],
#                     s3_bucket             = 's3.temp.universalsubtitles.org',
#                     installation_dir      = 'universalsubtitles.staging',
#                     static_dir            = '/var/static/tmp',
#                     name                  = 'staging',
#                     git_branch            = 'staging',
#                     memcached_bounce_cmd  = '/etc/init.d/memcached-staging restart',
#                     admin_dir             = '/usr/local/universalsubtitles.staging',
#                     admin_host            = 'pcf-us-admintmp.pculture.org:2191',
#                     celeryd_host          = 'pcf-us-admintmp.pculture.org:2191',
#                     celeryd_proj_root     = 'universalsubtitles.staging',
#                     separate_uslogging_db = True,
#                     celeryd_start_cmd     = "/etc/init.d/celeryd.staging start",
#                     celeryd_stop_cmd      = "/etc/init.d/celeryd.staging stop",
#                     celeryd_bounce_cmd    = "/etc/init.d/celeryd.staging restart &&  /etc/init.d/celeryevcam.staging start")
#
# def nf(username):
#     with Output("Configuring task(s) to run on NF env"):
#         _create_env(username              = username,
#                     hosts                 = ['nf.universalsubtitles.org:2191'],
#                     hostnames_squid_cache = ['nf.universalsubtitles.org',
#                                              'nf.amara.org'
#                                              ],
#                     s3_bucket             = 's3.nf.universalsubtitles.org',
#                     installation_dir      = 'universalsubtitles.nf',
#                     static_dir            = '/var/static/nf',
#                     name                  = 'nf',
#                     git_branch            = 'x-nf',
#                     memcached_bounce_cmd  = '/etc/init.d/memcached restart',
#                     admin_dir             = '/usr/local/universalsubtitles.nf',
#                     admin_host            = 'pcf-us-adminnf.pculture.org:2191',
#                     celeryd_host          = 'pcf-us-adminnf.pculture.org:2191',
#                     celeryd_proj_root     = 'universalsubtitles.nf',
#                     separate_uslogging_db = True,
#                     celeryd_start_cmd     = "/etc/init.d/celeryd start",
#                     celeryd_stop_cmd      = "/etc/init.d/celeryd stop",
#                     celeryd_bounce_cmd    = "/etc/init.d/celeryd restart &&  /etc/init.d/celeryevcam start")

def _reset_permissions(dir):
    sudo('chgrp {0} -R {1}'.format(env.app_group, dir))
    sudo('chmod -R g+w {0}'.format(dir))

def _git_pull():
    run('git checkout --force')
    run('git pull --ff-only')
    run('chgrp {0} -R .git 2> /dev/null; /bin/true'.format(env.app_group))
    run('chmod g+w -R .git 2> /dev/null; /bin/true')
    _reset_permissions('.')

def _git_checkout(commit, as_sudo=False):
    cmd = run
    if as_sudo:
        cmd = sudo
    cmd('git fetch')
    cmd('git checkout --force %s' % commit)
    cmd('chgrp {0} -R .git 2> /dev/null; /bin/true'.format(env.app_group))
    cmd('chmod g+w -R .git 2> /dev/null; /bin/true')
    _reset_permissions('.')

def _git_checkout_branch_and_reset(commit, branch='master', as_sudo=False):
    cmd = run
    if as_sudo:
        cmd = sudo
    cmd('git fetch')
    cmd('git checkout %s' % branch)
    cmd('git reset --hard %s' % commit)
    cmd('chgrp {0} -R .git 2> /dev/null; /bin/true'.format(env.app_group))
    cmd('chmod g+w -R .git 2> /dev/null; /bin/true')
    _reset_permissions('.')

@task
@lock_required
@runs_once
@roles('app')
def syncdb(extra=''):
    """Run python manage.py syncdb for the main and logging databases"""

    with Output("Syncing database") as out:
        with cd(env.app_dir):
            _git_pull()
            cmd = '{0}/bin/python manage.py syncdb {1} --settings=unisubs_settings'.format(\
                env.ve_dir, extra)
            #run('{0}/bin/python manage.py syncdb '
            #    '--settings=unisubs_settings'.format(env.ve_dir))
            run(cmd, pty=True)
            if env.separate_uslogging_db:
                run('{0}/bin/python manage.py syncdb '
                    '--database=uslogging --settings=unisubs_settings'.format(
                        env.ve_dir))
@task
@lock_required
@runs_once
@roles('app')
def migrate(app_name='', extra=''):
    with Output("Performing migrations"):
        with cd(env.app_dir):
            _git_pull()
            if env.separate_uslogging_db:
                run('{0}/bin/python manage.py migrate uslogging '
                    '--database=uslogging --settings=unisubs_settings'.format(
                        env.ve_dir))

            manage_cmd = 'yes no | {0}/bin/python -u manage.py migrate {1} {2} --settings=unisubs_settings 2>&1'.format(env.ve_dir, app_name, extra)
            timestamp_cmd = ADD_TIMESTAMPS.replace("'", r"\'")
            log_cmd = WRITE_LOG % 'database_migrations'

            cmd = (
                "screen sh -c $'" +
                    manage_cmd +
                    timestamp_cmd +
                    log_cmd +
                "'"
            )
            run(cmd)

@task
@lock_required
@parallel
@roles('app')
def update_environment(extra=''):
    with Output('Updating environment'):
        with cd(os.path.join(env.app_dir, 'deploy')):
            _git_pull()
            run('export PIP_REQUIRE_VIRTUALENV=true')
            # see http://lincolnloop.com/blog/2010/jul/1/automated-no-prompt-deployment-pip/
            run('yes i | {0}/bin/pip install {1} -r requirements.txt'.format(env.ve_dir, extra), pty=True)
            #_clear_permissions(os.path.join(base_dir, 'env'))

@task
@parallel
@roles('app')
def reload_app_servers():
    with Output("Reloading application servers"):
        """
        Reloading the app server will both make sure we have a
        valid commit guid (by running the create_commit_file)
        and also that we make the server reload code (currently
        with mod_wsgi this is touching the wsgi file)
        """
        with cd(env.app_dir):
            #run('{0}/bin/python deploy/create_commit_file.py'.format(env.ve_dir))
            run('touch deploy/unisubs.wsgi')

# Maintenance Mode
@task
@parallel
@roles('app')
def add_disabled():
    with Output("Putting the site into maintenance mode"):
        run('touch {0}/disabled'.format(env.app_dir))

@task
@parallel
@roles('app')
def remove_disabled():
    with Output("Taking the site out of maintenance mode"):
        run('rm {0}/disabled'.format(env.app_dir))