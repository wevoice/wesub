This repository is the code for the [Amara](http://amara.org) project.

The full documentation can be found at
http://amara.readthedocs.org/en/latest/index.html

[Amara]: http://amara.org

Quick Start
-----------

Amara uses [Docker](http://docker.io).  For ease of development, we use the docker-compose tool to have a full, production like, local dev environment.

1. Git clone the repository:

        git clone git://github.com/pculture/unisubs.git unisubs

   Now the entire project will be in the unisubs directory.

2. Install docker-compose (http://docs.docker.com/compose/install/)

3. Build the Amara docker image:

        bin/dev build

4. Start Amara Containers:

        bin/dev up

5. Configure Database:

        bin/dev dbreset

6. Add `unisubs.example.com` to your hosts file, pointing at `127.0.0.1`.  This
   is necessary for Twitter and Facebook oauth to work correctly.

   You can access the site at <http://unisubs.example.com:8000>.

To see services logs, run `docker-compose logs <service>` i.e. `docker-compose logs worker`

Testing
-------

To run the test suite:

        bin/dev test


Dev Notes
---------

To run a single `manage.py` command:

        bin/dev manage <command>

To see running services:

        docker-compose ps

To stop and remove all containers:

        docker-compose kill ; docker-compose rm

To view logs from a service:

        docker-compose logs <service>

To create an admin user:

        bin/dev manage createsuperuser
        
        
<a href="https://zenhub.com"><img src="https://raw.githubusercontent.com/ZenHubIO/support/master/zenhub-badge.png"></a>
