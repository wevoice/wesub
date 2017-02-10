#!/usr/bin/env python
# Amara, universalsubtitles.org
#
# Copyright (C) 2015 Participatory Culture Foundation
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

"""deploy.py -- Deployment script.

We use docker containers to deploy amara.  We use several types of containers:

    - App containers handle HTTP requests using uwsgi
    - Workers run celery tasks.  We currently have 2 kinds of workers:
        - The master worker runs most tasks and schedules periodic tasks
        - The feed worker runs the feed updates
    - We also create short-lived containers to run various build tasks like
      build_media and migrate

Containers run on different hosts:
    BUILDER_DOCKER_HOST -- the docker host running builder.amara.org.
        This is responsible for building the images and running preview
        builds.
    DOCKER_HOSTS -- Docker hosts that run app servers.  We try to spread
        the load evenly among them
    DOCKER_HOST_1 - Runs the master worker
    DOCKER_HOST_2 - Runs the feed worker
"""

import collections
import httplib
import itertools
import json
import os
import re
import socket
import subprocess
import sys
import time
import traceback
import urllib
import urlparse

# Host that runs builder.amara.org
BUILDER_DOCKER_HOST = 'unix:///docker.sock'

def log(msg, *args, **kwargs):
    log_nostar("* " + msg, *args, **kwargs)

def log_nostar(msg, *args, **kwargs):
    sys.stdout.write(msg.format(*args, **kwargs))
    sys.stdout.write("\n")
    sys.stdout.flush()

class LoggingTimer(object):
    """Measure times and write them to stdout."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.start_time = time.time()

    def log_time(self, msg, *args, **kwargs):
        total_time = time.time() - self.start_time
        mins, secs = divmod(total_time, 60)
        msg = msg.format(*args, **kwargs)
        log("{}: {}:{:0.1f}s", msg, int(mins), secs)
        self.reset()

ContainerInfo = collections.namedtuple('ContainerInfo', 'host name cid')

class UnixDomainSocketHTTPConnection(httplib.HTTPConnection):
    """HTTPConnection that uses a unix-domain socket

    We need this to use to docker remote API for the builder host
    """

    def __init__(self, path):
        httplib.HTTPConnection.__init__(self, '127.0.0.1')
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.path)

class Environment(object):
    """Fetching environment variables.

    This class does 2 things:
        - Presents a slightly nicer interface for getting env vars (attribute
          access instead of dict access)
        - Runs a sanity check to make sure we have the variables we need.
    """

    env_var_names = [
        # Global jenkins config
        'AWS_ACCESS_ID',
        'AWS_SECRET_KEY',
        'STAGING_AWS_ACCESS_ID',
        'STAGING_AWS_SECRET_KEY',
        'PRODUCTION_AWS_ACCESS_ID',
        'PRODUCTION_AWS_SECRET_KEY',
        'DOCKER_AUTH_EMAIL',
        'DOCKER_AUTH_PASSWORD',
        'DOCKER_AUTH_USERNAME',
        'DOCKER_HOST_1',
        'DOCKER_HOST_2',
        'DOCKER_HOSTS',
        'NEW_RELIC_LICENSE_KEY',
        'PRODUCTION_NUM_INSTANCES',
        # Build config/parameters
        'BUILD_NUMBER',
        'BRANCH',
        'MIGRATIONS',
    ]

    optional_env_var_names = [
        'ROLLBACK_ID',
        'DB_NAME',
        'RESET_DB',
    ]

    valid_migrate_values = [
        'DONT_MIGRATE',
        'MIGRATE_WHILE_RUNNING_OLD_CODE',
        'STOP_SERVERS_TO_MIGRATE'
    ]

    def __init__(self, needs_migrations=True):
        for name in self.env_var_names + self.optional_env_var_names:
            setattr(self, name, os.environ.get(name, ''))
        missing = [
            name for name in self.env_var_names
            if not getattr(self, name)
        ]
        if not needs_migrations and 'MIGRATIONS' in missing:
            missing.remove('MIGRATIONS')
        if missing:
            log("ENV variable(s) missing:")
            for name in missing:
                log("    {}", name)
            sys.exit(1)
        if (self.MIGRATIONS not in self.valid_migrate_values and
            needs_migrations):
            log("Invalid MIGRATIONS value: {}", self.MIGRATIONS)
            sys.exit(1)

    def docker_hosts(self):
        return self.DOCKER_HOSTS.split()

    def aws_credentials(self, limited=False):
        if not limited:
            return (self.AWS_ACCESS_ID, self.AWS_SECRET_KEY)
        if self.BRANCH == 'production':
            return (self.PRODUCTION_AWS_ACCESS_ID,
                    self.PRODUCTION_AWS_SECRET_KEY)
        else:
            return (self.STAGING_AWS_ACCESS_ID, self.STAGING_AWS_SECRET_KEY)

class Docker(object):
    """Run docker commands.  """

    def _build_command_line(self, host, cmdline):
        return [ 'docker', '-H', host ] + list(cmdline)

    def run(self, host, *cmdline):
        """Run a docker command."""
        full_cmdline = self._build_command_line(host, cmdline)
        log("{}", ' '.join(full_cmdline))
        subprocess.check_call(full_cmdline)

    def run_and_return_output(self, host, *cmdline):
        """Run a docker command."""
        full_cmdline = self._build_command_line(host, cmdline)
        log("{}", ' '.join(full_cmdline))
        return subprocess.check_output(full_cmdline)

    def Popen(self, host, *cmdline, **popen_args):
        """Run a docker command."""
        full_cmdline = self._build_command_line(host, cmdline)
        log("{}", ' '.join(full_cmdline))
        return subprocess.Popen(full_cmdline, **popen_args)

    def get_http_response(self, host, path, query=None):
        parsed_url = urlparse.urlparse(host)
        if parsed_url.scheme == 'tcp':
            host, port = parsed_url.netloc.split(":")
            conn = httplib.HTTPConnection(host, port)
        elif parsed_url.scheme == 'unix':
            conn = UnixDomainSocketHTTPConnection(parsed_url.path)
        else:
            raise ValueError("Unknown host type: {}", host)
        if query:
            path += '?{}'.format(urllib.urlencode(query))
        conn.request('GET', path)
        return conn.getresponse()

    def remote_api_get(self, host, path, query=None):
        return json.load(self.get_http_response(host, path, query))

    def get_containers(self, host, **filters):
        """Get a list of docker containers on a host.

        Returns:
            List of dicts containing info on the containers.
        """
        query = {
            'all': '1',
        }
        if filters:
            query['filters'] = json.dumps(filters)
        return self.remote_api_get(host, '/containers/json', query)

    def get_container_details(self, host, cid):
        """Get details about a container."""
        return self.remote_api_get(host, '/containers/{}/json'.format(cid))

    def get_images(self, host):
        """Get a list of docker images on a host.

        Returns:
            List of dicts containing info on the images.
        """
        return self.remote_api_get(host, '/images/json')

    def image_exists(self, host, image_id):
        path = '/images/{}/json'.format(image_id)
        response = self.get_http_response(host, path)
        return response.status == 200

class ImageBuilder(object):
    """Build images and distribute them to our hosts."""
    def __init__(self, env, commit_id):
        self.docker = Docker()
        self.env = env
        self.commit_id = commit_id
        self.image_name = 'amara:{}'.format(commit_id)

    def tag_name(self):
        return 'amara-{}:latest'.format(self.env.BRANCH)

    def setup_images(self):
        timer = LoggingTimer()
        # make sure amara-enterprise is on the correct commit
        subprocess.check_call(['bin/update-integration.py', '--skip-fetch'])
        subprocess.check_call(['bin/build.py', self.image_name])
        timer.log_time('image build')
        # Send the image from builder to the other docker hosts
        log('sending image from builder to docker hosts')
        save_proc = self.docker.Popen(BUILDER_DOCKER_HOST, 'save',
                                      self.image_name, stdout=subprocess.PIPE)
        load_procs = [
            self.docker.Popen(host, 'load', stdin=subprocess.PIPE)
            for host in self.env.docker_hosts()
        ]
        BUF_SIZE = 4096
        while True:
            data = save_proc.stdout.read(BUF_SIZE)
            if not data:
                break
            for proc in load_procs:
                proc.stdin.write(data)
        for proc in load_procs:
            proc.stdin.close()
        if save_proc.wait() != 0:
            raise subprocess.CalledProcessError(
                "docker save error: {}".format(save_proc.return_code))
        for proc in load_procs:
            if proc.wait() != 0:
                raise subprocess.CalledProcessError(
                    "docker load error: {}".format(proc.return_code))
        timer.log_time('image save/load')
        if self.env.BRANCH in ('staging', 'production'):
            # Tag the image with amara-<branch>:latest
            # We use the tags to run periodic tasks, like updating
            # translations
            for host in [BUILDER_DOCKER_HOST] + self.env.docker_hosts():
                self.docker.run(host, 'tag', self.image_name, self.tag_name())

class ContainerManager(object):
    """Start/stop docker containers """

    def __init__(self, env, commit_id, image_name):
        self.docker = Docker()
        self.env = env
        self.commit_id = commit_id
        self.image_name = image_name
        self.containers_started = []
        self.containers_stopped = []

    def building_preview(self):
        return self.env.BRANCH not in ('staging', 'production')

    def app_params(self, limited=False):
        """Get docker params to used for both app containers and workers
        """
        aws_access_id, aws_secret_key = self.env.aws_credentials(limited)
        params = [
            # AWS Auth info
            '-e', 'AWS_ACCESS_ID=' + aws_access_id,
            '-e', 'AWS_SECRET_KEY=' + aws_secret_key,
            # REVISION controls the git revision we check out before starting
            # this is actually somewhat redundant since we already copy the
            # files into the docker image
            '-e', 'REVISION=' + self.env.BRANCH,
            # mount the workspace volume inside our container
            '-v', '/var/workspace:/var/workspace',
        ]
        if self.env.DB_NAME:
            params.extend([
                '-e', 'DB_NAME=' + self.env.DB_NAME,
            ])

        if self.building_preview():
            # SETTINGS_REVISION controls how to download the
            # server_local_settings.py file (see .docker/config_env.sh)
            params.extend(['-e', 'SETTINGS_REVISION=staging'])
        return params

    def interlock_params(self):
        if self.env.BRANCH == 'production':
            return [
                '-e', ('INTERLOCK_DATA={"alias_domains": '
                       '["www.amara.org"]}'),
                '-e', 'NEW_RELIC_APP_NAME=AmaraVPC',
                '-e', ('NEW_RELIC_LICENSE_KEY=' +
                       self.env.NEW_RELIC_LICENSE_KEY)
            ]
        else:
            return []

    def app_hostname(self):
        """Hostname for app containers.

        The hostname sets an entry in the hosts file for the container.  But
        more importantly, it tells Interlock what web traffic should be routed
        to the container.
        """
        if self.env.BRANCH == 'production':
            return 'amara.org'
        else:
            return '{}.amara.org'.format(self.env.BRANCH)

    def container_name_prefix_for_branch(self):
        """Start of docker container names for this git branch."""
        return 'app-amara-{}-'.format(self.env.BRANCH)

    def container_name_prefix_for_build(self):
        """Start of docker container names for this particular build. """
        # Include both the git commit ID and the build number since both could
        # be useful.
        return self.container_name_prefix_for_branch() + '{}-{}-'.format(
            self.commit_id[:6], self.env.BUILD_NUMBER)

    def run_app_command(self, command, argument=None):
        """Run a command using the app container

        Use this to run a command that does something then quits like
        build_media or migrate.

        Args:
            command: command to pass to our entrypoint.  The entrypoint is a
                copy of .docker/entry.sh
        """
        cmd_line = [ 'run', '-t', '--rm', ]
        cmd_line += self.app_params()
        cmd_line += [self.image_name, command]
        if argument is not None:
            cmd_line += [argument]
        self.docker.run(self.env.DOCKER_HOST_1, *cmd_line)

    def start_worker_container(self, host, name, command):
        """Start an app contanier running the feed/master worker

        Args:
            host: docker host
            name: docker name suffix of the container.  This is what shows up
                in docker ps.  All names will be prefixed with
                container_name_prefix_for_build().
            command: command to pass to our entry point (feed_worker, or
                master_worker)

        """
        host_name = '{}-{}.amara.org'.format(self.env.BRANCH, name)
        name = self.container_name_prefix_for_build() + name
        cmd_line = [
            'run', '-t', '-d',
            '-h', host_name,
            '--name', name,
            '--restart=always',
        ] + self.app_params(limited=True) + [self.image_name, command]
        cid = self.docker.run_and_return_output(host, *cmd_line).strip()
        log("container id: {}", cid)
        self.containers_started.append(ContainerInfo(host, name, cid))

    def start_app_container(self, host, name):
        """Start an app contanier running a web server

        Args:
            host: docker host
            name: docker name suffix of the container.  This is what shows up
                in docker ps.  All names will be prefixed with
                container_name_prefix_for_build().
        """
        name = self.container_name_prefix_for_build() + name
        cmd_line = [
            'run', '-t', '-d', '-P',
            '-h', self.app_hostname(),
            '--name', name,
            '--restart=always',
        ] + self.app_params(limited=True) + self.interlock_params() + [self.image_name]
        cid = self.docker.run_and_return_output(host, *cmd_line).strip()
        log("container id: {}", cid)
        self.containers_started.append(ContainerInfo(host, name, cid))

    def start_new_containers(self):
        """Start docker containers for this deploy."""

        if self.env.BRANCH == 'production':
            # for production we start up many instances, spread across the
            # hosts
            host_iter = itertools.cycle(self.env.docker_hosts())
            for i in range(int(self.env.PRODUCTION_NUM_INSTANCES)):
                host = host_iter.next()
                self.start_app_container(host, str(i + 1))
        elif self.env.BRANCH == 'staging':
            # for staging we start up 1 instance per host
            for i, host in enumerate(self.env.docker_hosts()):
                self.start_app_container(host, str(i + 1))
        else:
            # for preview branches we start 1 instance on the builder host.
            # Also we don't start up the workers
            self.start_app_container(BUILDER_DOCKER_HOST, 'preview')
            return

        self.start_worker_container(self.env.DOCKER_HOST_1, 'master-worker',
                                    'master_worker')
        self.start_worker_container(self.env.DOCKER_HOST_2, 'feed-worker',
                                    'feed_worker')

    def find_old_containers(self):
        """Find containers started by previous deploys.

        Returns a list of (host, container_id) tuples.
        """
        old_containers = []
        hosts_to_search = [BUILDER_DOCKER_HOST] + self.env.docker_hosts()
        for host in hosts_to_search:
            for container in self.docker.get_containers(host):
                try:
                    name = container['Names'][0]
                except KeyError:
                    pass
                if self.container_name_prefix_for_branch() in name:
                    cid = container['Id']
                    old_containers.append(ContainerInfo(host, name, cid))
        log("old app servers: {}", old_containers)
        return old_containers

    def shutdown_old_containers(self, old_containers):
        for container in old_containers:
            self.docker.run(container.host, 'kill', container.cid)
            self.containers_stopped.append(container)

    def remove_old_app_servers(self, old_containers):
        for container in old_containers:
            self.docker.run(container.host, 'rm', '-v', container.cid)

    def print_report(self):
        line_fmt = "{:<60} {:<60} {:<64}"
        log("------------- Containers Stopped ---------------")
        log(line_fmt, 'Host', 'Name', 'Container ID')
        for container in self.containers_stopped:
            log(line_fmt, *container)
        log("------------- Containers Started ---------------")
        log(line_fmt, 'Host', 'Name', 'Container ID')
        for container in self.containers_started:
            log(line_fmt, *container)
        log("------------- Shell Command Line ---------------")
        cmd_line = [
            'docker', 'run', '-it', '--rm',
        ] + self.app_params() + [self.image_name, 'shell']
        log_nostar(' '.join(cmd_line))

class Deploy(object):
    """Top-level manager for the deploy."""
    def run(self):
        self.setup()
        if not self.env.ROLLBACK_ID:
            self.image_builder.setup_images()
        if self.env.RESET_DB == 'true':
            if self.container_manager.building_preview():
                self.container_manager.run_app_command("reset_db")
            else:
                log("Not calling reset_db since we are not "
                    "building a preview.")
        if not self.env.ROLLBACK_ID:
            self.container_manager.run_app_command("build_media")
        self.start_and_stop_containers()
        if self.container_manager.building_preview():
            self.container_manager.run_app_command("setup_preview_site", argument=self.container_manager.app_hostname())
        self.container_manager.print_report()

    def build(self):
        self.setup(needs_migrations=False)
        self.image_builder.setup_images()
        self.container_manager.run_app_command("build_media")
        self.container_manager.print_report()

    def stop_old_containers(self):
        self.setup()
        old_containers = self.container_manager.find_old_containers()
        self.container_manager.shutdown_old_containers(old_containers)

    def setup(self, needs_migrations=True):
        self.cd_to_project_root()
        self.env = Environment(needs_migrations)
        commit_id = self.get_commit_id()
        self.image_builder = ImageBuilder(self.env, commit_id)
        self.container_manager = ContainerManager(
            self.env, commit_id, self.image_builder.image_name)

    def get_commit_id(self):
        if self.env.ROLLBACK_ID:
            log("Getting commit ID from ROLLBACK_ID")
            commit_id = self.env.ROLLBACK_ID
        else:
            cmd = ["git", "rev-parse", "HEAD"]
            commit_id = subprocess.check_output(cmd).strip()
        if not re.match('^[0-9a-f]{40}$', commit_id):
            raise ValueError("Invalid commit id: {}".format(commit_id))
        return commit_id

    def cd_to_project_root(self):
        project_root = os.path.abspath(
            os.path.dirname(os.path.dirname(__file__))
        )
        log('cd to {}', project_root)
        os.chdir(project_root)

    def start_and_stop_containers(self):
        old_containers = self.container_manager.find_old_containers()
        if self.env.MIGRATIONS == 'DONT_MIGRATE':
            self.container_manager.start_new_containers()
            time.sleep(30)
            self.container_manager.shutdown_old_containers(old_containers)
        elif self.env.MIGRATIONS == 'MIGRATE_WHILE_RUNNING_OLD_CODE':
            self.container_manager.run_app_command('migrate')
            self.container_manager.start_new_containers()
            time.sleep(30)
            self.container_manager.shutdown_old_containers(old_containers)
        elif self.env.MIGRATIONS == 'STOP_SERVERS_TO_MIGRATE':
            self.container_manager.shutdown_old_containers(old_containers)
            self.container_manager.run_app_command('migrate')
            self.container_manager.start_new_containers()
        else:
            raise ValueError("Unknown MIGRATIONS value: {}".format(
                self.env.MIGRATIONS))
        # give containers some time to shutdown before we remove them
        time.sleep(5)
        self.container_manager.remove_old_app_servers(old_containers)


class Cleanup(object):
    def run(self):
        docker_hosts = self.get_docker_hosts()
        self.docker = Docker()
        for host in [BUILDER_DOCKER_HOST] + docker_hosts:
            log("Host: {}", host)
            self.remove_stopped_containers(host)
            self.remove_unused_images(host)

    def get_docker_hosts(self):
        try:
            return os.environ['DOCKER_HOSTS'].split()
        except KeyError:
            log("DOCKER_HOSTS ENV variable missing")
            sys.exit(1)

    def remove_stopped_containers(self, host):
        log("checking for stoped containers")
        for container in self.docker.get_containers(host, status=['exited']):
            log("removing stopped container: {}", container['Id'])
            self.docker.run(host, 'rm', '-v', container['Id'])


    def remove_image(self, host, image):
        try:
            self.docker.run(host, 'rmi', image)
        except subprocess.CalledProcessError:
            # removing an image can fail if another container was started that
            # uses the image after get the list.  Just print a warning and
            # continue on
            log("Warning: error removing image {}", image)

    def remove_unused_images(self, host):
        log("checking for unused images")
        container_ids = [
        ]

        used_images = collections.defaultdict(list)
        for container in self.docker.get_containers(host):
            cid = container['Id']
            details = self.docker.get_container_details(host, cid)
            used_images[details['Image']].append(details['Name'])

        for image_info in self.docker.get_images(host):
            image = image_info['Id']
            tags = [
                tag for tag in image_info['RepoTags']
                if tag != '<none>:<none>'
            ]
            if self.should_skip_image(image, tags):
                continue

            if image in used_images:
                log("Image {} in use {}", image, used_images[image])
            else:
                for tag in tags:
                    log("Untagging {}", tag)
                    self.remove_image(host, tag)
                if self.docker.image_exists(host, image):
                    log("removing unused image: {}", image)
                    self.remove_image(host, image)
                else:
                    log("image removed from untagging: {}", image)

    def should_skip_image(self, image, tags):
        for tag in tags:
            if tag.endswith(":latest"):
                log("skipping {} because of tag {}", image, tag)
                return True
        return False

def main(argv):
    try:
        try:
            command = argv[1].lower()
        except IndexError:
            command = 'deploy'
        if command == 'deploy':
            Deploy().run()
        elif command == 'stop-deploy':
            Deploy().stop_old_containers()
        elif command == 'build':
            Deploy().build()
        elif command == 'cleanup':
            Cleanup().run()
        else:
            log.write("Unknown command: {}", command)
            sys.exit(1)
    except Exception, e:
        sys.stderr.write("Error: {}\n{}".format(
            e, ''.join(traceback.format_exc())))
        sys.exit(1)

if __name__ == '__main__':
    main(sys.argv)
