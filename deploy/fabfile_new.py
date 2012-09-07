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
from fabric.tasks import execute
from fabric.context_managers import settings, hide
from fabric.utils import fastprint
from fabric.decorators import roles, runs_once, parallel
import fabric.state

ADD_TIMESTAMPS = """ | awk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $0; fflush(); }' """
WRITE_LOG = """ | tee /tmp/%s.log """

# hide 'running' by default
fabric.state.output['running'] = False

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
        host = '({0})'.format(env.host) if env.host else ''
        self.message = '{0} {1}'.format(message, host)

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

def _notify(subj, msg, to):
    run("echo '{1}' | mailx -s '{0}' {2}".format(subj, msg, to))

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
        _unlock()

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
                key_filename=env.key_filename,
                roledefs={},
                notification_email=None):
    env.user = username
    env.name = name
    env.environment = name
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
    env.notification_email = notification_email or 'universalsubtitles-dev@pculture.org'

@task
def local(username='vagrant', key='~/.vagrant.d/insecure_private_key'):
    """
    Configure task(s) to run in the local environment

    """
    with Output("Configuring task(s) to run on LOCAL"):
        _create_env(username              = username,
                    name                  = 'local',
                    s3_bucket             = 's3.local.amara.org',
                    app_name              = 'unisubs',
                    app_dir               = '/opt/apps/local/unisubs/',
                    app_group             = 'deploy',
                    revision              = 'staging',
                    ve_dir                = '/opt/ve/local/unisubs',
                    separate_uslogging_db = False,
                    key_filename          = key,
                    roledefs              = {
                        'app': ['10.10.10.115'],
                        'data': ['10.10.10.120'],
                    },
                    notification_email   = 'ehazlett@pculture.org',)

@task
def dev(username):
    """
    Configure task(s) to run in the dev environment

    """
    with Output("Configuring task(s) to run on DEV"):
        env_name = 'dev'
        _create_env(username              = username,
                    name                  = env_name,
                    s3_bucket             = None,
                    app_name              = 'unisubs',
                    app_dir               = '/opt/apps/{0}/unisubs/'.format(
                        env_name),
                    app_group             = 'deploy',
                    revision              = env_name,
                    ve_dir                = '/opt/ve/{0}/unisubs'.format(
                        env_name),
                    separate_uslogging_db = False,
                    roledefs              = {
                        'app': ['app-00-dev.amara.org'],
                        'data': ['data-00-dev.amara.org'],
                    },
                    notification_email   = 'ehazlett@pculture.org',)

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

def _reset_permissions(app_dir):
    sudo('chgrp -R {0} {1}'.format(env.app_group, app_dir))
    sudo('chmod -R g+w {0}'.format(app_dir))

@task
@roles('app', 'data')
def reset_permissions():
    _reset_permissions(env.app_dir)
    _reset_permissions(env.ve_dir)

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

def _git_checkout_branch_and_reset(commit, branch='dev', run_as_sudo=False):
    cmd = run
    if run_as_sudo:
        cmd = sudo
    cmd('git fetch')
    cmd('git checkout %s' % branch)
    cmd('git reset --hard %s' % commit)
    cmd('chgrp {0} -R .git 2> /dev/null; /bin/true'.format(env.app_group))
    cmd('chmod g+w -R .git 2> /dev/null; /bin/true')
    _reset_permissions('.')

def _get_optional_repo_version(app_dir, repo):
    '''Find the optional repo version by looking at its file in optional/.'''
    with cd(os.path.join(app_dir, 'optional')):
        return run('cat {0}'.format(repo))

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
@roles('app', 'data')
def update_environment(extra=''):
    with Output('Updating environment'):
        with cd(os.path.join(env.app_dir, 'deploy')):
            _git_pull()
            run('export PIP_REQUIRE_VIRTUALENV=true')
            # see http://lincolnloop.com/blog/2010/jul/1/automated-no-prompt-deployment-pip/
            run('yes i | {0}/bin/pip install {1} -r requirements.txt'.format(env.ve_dir, extra), pty=True)
            _reset_permissions(env.app_dir)
        with cd(env.app_dir):
            run('{0}/bin/python deploy/create_commit_file.py'.format(env.ve_dir))

@task
@parallel
@roles('app')
def reload_app_servers(hard=False):
    with Output("Reloading application servers"):
        """
        Reloading the app server will both make sure we have a
        valid commit guid (by running the create_commit_file)
        and also that we make the server reload code (currently
        with mod_wsgi this is touching the wsgi file)
        """
        if hard:
            sudo('service uwsgi.unisubs.{0} restart'.format(env.environment))
        else:
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

@task
@parallel
@roles('app', 'data')
def update_integration(run_as_sudo=True, branch=None):
    '''Update the integration repo to the version recorded in the site repo.

    At the moment it is assumed that the optional/unisubs-integration file
    exists, and that the unisubs-integration repo has already been cloned down.

    The file should contain the commit hash and nothing else.

    TODO: Run this from update_web automatically

    '''
    branch = branch if branch is not None else env.revision
    with Output("Updating nested unisubs-integration repositories"):
        with cd(os.path.join(env.app_dir, 'unisubs-integration')), \
            settings(warn_only=True):
            _git_checkout_branch_and_reset(
                _get_optional_repo_version(env.app_dir, 'unisubs-integration'),
                branch=branch,
                run_as_sudo=run_as_sudo
            )

@task
@lock_required
@runs_once
@roles('data')
def update_solr_schema():
    '''Update the Solr schema and rebuild the index.

    The rebuilding will be done asynchronously with screen and an email will
    be sent when it finishes.

    '''
    with Output("Updating Solr schema (and rebuilding the index)"):
        python_exe = '{0}/bin/python'.format(env.ve_dir)
        with cd(env.app_dir):
            _git_pull()
            run('{0} manage.py build_solr_schema --settings=unisubs_settings > /etc/solr/conf/{1}/conf/schema.xml'.format(
                    python_exe,
                    env.environment))
            run('{0} manage.py reload_solr_core --settings=unisubs_settings'.format(python_exe))
            sudo('service tomcat6 restart')

        # Fly, you fools!

        managepy_file = os.path.join(env.app_dir, 'manage.py')

        # The -u here is for "unbuffered" so the lines get outputted immediately.
        manage_cmd = '%s -u %s rebuild_index_ordered --noinput --settings=unisubs_settings 2>&1' % (python_exe, managepy_file)
        mail_cmd = ' | mail -s Solr_index_rebuilt_on_%s %s' % (env.host_string, env.notification_email)
        log_cmd = WRITE_LOG % 'solr_reindexing'

        # The single quotes in the ack command needs to be escaped, because
        # we're in a single quoted ANSI C-style string from the sh -c in the
        # screen command.
        #
        # We can't use a double quoted string for the sh -c call because of the
        # $0 in the ack script.
        timestamp_cmd = ADD_TIMESTAMPS.replace("'", r"\'")

        cmd = (
            "screen -d -m sh -c $'" +
                manage_cmd +
                timestamp_cmd +
                log_cmd +
                mail_cmd +
            "'"
        )

        run(cmd, pty=False)

@task
@parallel
@roles('app')
def bounce_memcached():
    '''Bounce memcached (purging the cache).

    Should be done at the end of each deploy.

    '''
    with Output("Bouncing memcached"):
        sudo('service memcached stop')
        sudo('service memcached start')

@task
@parallel
@roles('data')
def bounce_celery():
    '''Bounce celery daemons.

    Should be done at the end of each deploy.

    '''
    with Output("Bouncing celeryd"):
        with settings(warn_only=True):
            sudo('service celeryd.{0} stop'.format(env.environment))
            sudo('service celeryd.{0} start'.format(env.environment))
    with Output("Bouncing celerycam"):
        with settings(warn_only=True):
            sudo('service celerycam.{0} stop'.format(env.environment))
            sudo('service celerycam.{0} start'.format(env.environment))

@task
@lock_required
@roles('app', 'data')
def deploy(branch=None, integration_branch=None, skip_celery=False):
    """
    This is how code gets reloaded:

    - Checkout code on the auxiliary server ADMIN whost
    - Checkout the latest code on all appservers
    - Remove all pyc files from app servers
    - Bounce celeryd, memcached , test services
    - Reload app code (touch wsgi file)

    Until we implement the checking out code to an isolated dir
    any failure on these steps need to be fixed or will result in
    breakage
    """
    with Output("Updating the main unisubs repo"), cd(env.app_dir):
        if branch:
            _switch_branch(branch)
        else:
            _git_pull()

    with Output("Updating integration repo"):
        execute(update_integration, branch=integration_branch)
        with cd(env.app_dir):
            with settings(warn_only=True):
                run("find . -name '*.pyc' -delete")

    if skip_celery == False:
        execute(bounce_celery)
    execute(bounce_memcached)
    #test_services()
    execute(reload_app_servers)

    #if env.environment not in ['dev']:
    _notify("Amara {0} deployment".format(env.environment), "Deployed by {0} to {1} at {2} UTC".format(env.user,  environment, datetime.utcnow()))

@task
@lock_required
@runs_once
@roles('app')
def update_static_media(compilation_level='ADVANCED_OPTIMIZATIONS', skip_compile=False, skip_s3=False):
    """
    Compiles and uploads static media to S3

    :param compilation_level: Level of optimization (default: ADVANCED_OPTIMIZATIONS)
    :param skip_s3: Skip upload to S3 (default: False)

    """
    with Output("Updating static media") as out, cd(env.app_dir):
        media_dir = '{0}/media/'.format(env.app_dir)
        python_exe = '{0}/bin/python'.format(env.ve_dir)
        _git_pull()
        execute(update_integration)
        run('{0} deploy/create_commit_file.py'.format(python_exe))
        if skip_compile == False:
            out.fastprintln('Compiling...')
            with settings(warn_only=True):
                run('{0} manage.py  compile_media --compilation-level={1} --settings=unisubs_settings'.format(python_exe, compilation_level))
        if env.environment != 'dev' and skip_s3 == False:
            out.fastprintln('Uploading to S3...')
            run('{0} manage.py  send_to_s3 --settings=unisubs_settings'.format(python_exe))

@task
@runs_once
@roles('data')
def update_django_admin_media():
    """
    Uploads Django Admin static media to S3

    """
    with Output("Uploading Django admin media"):
        media_dir = '{0}/lib/python2.6/site-packages/django/contrib/admin/media/'.format(env.ve_dir)
        python_exe = '{0}/bin/python'.format(env.ve_dir)
        s3_bucket = 's3.{0}.amara.org/admin/'.format(env.environment)
        sudo('s3cmd -P -c /etc/s3cfg sync {0} s3://{1}'.format(media_dir, s3_bucket))

@task
@roles('app')
def update_django_admin_media_dev():
    """
    Uploads Django Admin static media for dev

    This is separate from the update_django_admin_media task as this needs to
    run on each webserver for the dev environment.

    """
    with Output("Copying Django Admin static media"), cd(env.app_dir):
        media_dir = '{0}/lib/python2.6/site-packages/django/contrib/admin/media/'.format(env.ve_dir)
        python_exe = '{0}/bin/python'.format(env.ve_dir)
        # copy media to local dir
        run('cp -r {0} ./media/admin'.format(media_dir))

def _switch_branch(branch):
    with cd(env.app_dir), settings(warn_only=True):
        run('git fetch')
        run('git branch --track {0} origin/{0}'.format(branch))
        run('git checkout {0}'.format(branch))
        _git_pull()
@task
@parallel
@roles('app', 'data')
def switch_branch(branch):
    """
    Switches the current branch

    :param branch: Name of branch to switch

    """
    with Output('Switching to {0}'.format(branch)):
        _switch_branch(branch)

@task
def demo(revision='dev', host='app-00-dev.amara.org', \
    repo='https://github.com/pculture/unisubs.git', integration_revision='dev'):
    """
    Deploys the specified revision for live testing

    :param revision: Revision to test
    :param host: Test host (default: app-00-dev.amara.org)

    """
    env.host_string = host
    with Output("Deploying demo version {0} to {1}".format(revision, host)) as out:
        # remove existing deployment if present
        with settings(warn_only=True):
            execute(remove_demo, revision=revision, host=host)
        run('mkdir -p /var/tmp/{0}'.format(revision))
        out.fastprintln('Creating Nginx config')
        # nginx config
        run('cp /etc/nginx/conf.d/amara_dev.conf /tmp/{0}.conf'.format(revision))
        run("sed -i 's/server_name.*;/server_name {0}.demo.amara.org;/g' /tmp/{0}.conf".format(\
            revision))
        run("sed -i 's/root \/opt\/apps\/dev/root \/var\/tmp\/{0}/g' /tmp/{0}.conf".format(\
            revision))
        run("sed -i 's/uwsgi_pass.*;/uwsgi_pass unix:\/\/\/tmp\/uwsgi_{0}.sock;/g' /tmp/{0}.conf".format(\
            revision))
        sudo("mv /tmp/{0}.conf /etc/nginx/conf.d/{0}.conf".format(revision))
        out.fastprintln('Configuring uWSGI')
        # uwsgi ini
        run('cp /etc/uwsgi.unisubs.dev.ini /tmp/uwsgi.unisubs.{0}.ini'.format(revision))
        run("sed -i 's/socket.*/socket = \/tmp\/uwsgi_{0}.sock/g' /tmp/uwsgi.unisubs.{0}.ini".format(\
            revision))
        run("sed -i 's/virtualenv.*/virtualenv = \/var\/tmp\/{0}\/ve/g' /tmp/uwsgi.unisubs.{0}.ini".format(\
            revision))
        run("sed -i 's/wsgi-file.*/wsgi-file = \/var\/tmp\/{0}\/unisubs\/deploy\/unisubs.wsgi/g' /tmp/uwsgi.unisubs.{0}.ini".format(\
            revision))
        run("sed -i 's/log-syslog.*/log-syslog = uwsgi.unisubs.{0}/g' /tmp/uwsgi.unisubs.{0}.ini".format(\
            revision))
        run("sed -i 's/touch-reload.*/touch-reload = \/var\/tmp\/{0}\/unisubs\/deploy\/unisubs.wsgi/g' /tmp/uwsgi.unisubs.{0}.ini".format(\
            revision))
        run("sed -i 's/pythonpath.*/pythonpath = \/var\/tmp\/{0}/g' /tmp/uwsgi.unisubs.{0}.ini".format(\
            revision))
        # uwsgi upstart
        run('cp /etc/init/uwsgi.unisubs.dev.conf /tmp/uwsgi.unisubs.{0}.conf'.format(revision))
        run("sed -i 's/exec.*/exec uwsgi --ini \/var\/tmp\/{0}\/uwsgi.unisubs.{0}.ini/g' /tmp/uwsgi.unisubs.{0}.conf".format(revision))
        sudo("mv /tmp/uwsgi.unisubs.{0}.conf /etc/init/uwsgi.unisubs.demo.{0}.conf".format(revision))
        run('mv /tmp/uwsgi.unisubs.{0}.ini /var/tmp/{0}/uwsgi.unisubs.{0}.ini'.format(revision))
        out.fastprintln('Cloning repositories (unisubs & integration)')
        # clone
        run('git clone {1} /var/tmp/{0}/unisubs'.format(\
            revision, repo))
        with cd('/var/tmp/{0}/unisubs'.format(revision)):
            run('git checkout --force {0}'.format(revision))
        sudo('git clone git@github.com:pculture/unisubs-integration.git /var/tmp/{0}/unisubs/unisubs-integration'.format(revision))
        with cd('/var/tmp/{0}/unisubs/unisubs-integration'.format(revision)):
            sudo('git checkout --force {0}'.format(integration_revision))
        out.fastprintln('Building virtualenv')
        # build virtualenv
        run('virtualenv /var/tmp/{0}/ve'.format(revision))
        # install requirements
        with cd('/var/tmp/{0}/unisubs/deploy'.format(revision)):
            run('/var/tmp/{0}/ve/bin/pip install -r requirements.txt'.format(revision))
        # copy private config
        private_conf = '/var/tmp/{0}/unisubs/server_local_settings.py'.format(revision)
        run('cp /opt/apps/dev/unisubs/server_local_settings.py {0}'.format(private_conf))
        run("sed -i 's/MEDIA_URL.*/MEDIA_URL = \"http:\/\/{0}.demo.amara.org\/user-data\/\"/g' {1}".format(\
            revision, private_conf))
        run("sed -i 's/STATIC_URL.*/STATIC_URL = \"http:\/\/{0}.demo.amara.org\/site_media\/\"/g' {1}".format(\
            revision, private_conf))
        out.fastprintln('Compiling static media.  This may take a while.')
        # compile media
        # create a symlink to google closure library for compilation
        sudo('ln -sf /opt/google-closure /var/tmp/{0}/unisubs/media/js/closure-library'.format(revision))
        with cd('/var/tmp/{0}/unisubs'.format(revision)), settings(warn_only=True):
            python_exe = '/var/tmp/{0}/ve/bin/python'.format(revision)
            run('{0} deploy/create_commit_file.py'.format(python_exe))
            run('{0} manage.py  compile_media --compilation-level={1} --settings=unisubs_settings'.format(python_exe, 'ADVANCED_OPTIMIZATIONS'))
        out.fastprintln('Starting demo')
        sudo('service nginx reload')
        sudo('service uwsgi.unisubs.demo.{0} start'.format(revision))
        out.fastprintln('Done. Demo should be available at http://{0}.demo.amara.org'.format(revision))

@task
def remove_demo(revision='dev', host='app-00-dev.amara.org'):
    """
    Removes live testing demo

    :param revision: Revision that was used in launching the demo
    :param host: Test host (default: app-00-dev.amara.org)

    """
    env.host_string = host
    with Output("Removing {0} demo from {1}".format(revision, host)):
        # remove demo
        with settings(warn_only=True):
            sudo('service uwsgi.unisubs.demo.{0} stop'.format(revision))
        sudo('rm -rf /var/tmp/{0}'.format(revision))
        sudo('rm -f /etc/nginx/conf.d/{0}.conf'.format(revision))
        sudo('rm -f /etc/init/uwsgi.unisubs.demo.{0}.conf'.format(revision))
        sudo('service nginx reload')

