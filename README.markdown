This repository is the code for the [Amara][] project.

The full documentation can be found at
http://amara.readthedocs.org/en/latest/index.html

[Amara]: http://universalsubtitles.org

Quick Start
-----------

Amara uses [Vagrant][] to make it easy to get started.  If you've
never used Vagrant before we highly recommend going through its [quick start
guide][vagrant-guide] to learn how it works.

[Vagrant]: http://vagrantup.com/
[vagrant-guide]: http://vagrantup.com/docs/getting-started/index.html

To run the development version:

1. Git clone the repository:

        git clone git://github.com/pculture/unisubs.git unisubs

   Now the entire project will be in the unisubs directory.

2. Install VirtualBox and vagrant if you don't have them yet. Then type:

        vagrant up

   This is going to create a vm and provision it. It should take 10-15 minutes.
   Remember what mom said: a watched pot never boils.

3. Switch over to your vagrant vm with:

        vagrant ssh

   By default our `~/.bashrc` file will automatically move you to the shared
   folder and activate the virtualenv.

   Now run following command:

        ./bootstrap-vagrant.sh

   It's safe to run `bootstrap-vagrant.sh` multiple times if something goes
   wrong (like PyPi goes down).

4. Add `unisubs.example.com` to your hosts file, pointing at `127.0.0.1`.  This
   is necessary for Twitter and Facebook oauth to work correctly.

5. In your vagrant vm (the one you switched to in step 3), run the site with:

        ./dev-runserver.sh

   You can access the site at <http://unisubs.example.com:8000>.

Testing
-------

To run unit tests, use the `pmt` alias.  This will ensure that you're using the
correct settings for testing.

You can specify specific tests to run, just like if you were using `nosetests`.
For example:

    $ vagrant ssh

    # Just the tests in apps/teams/tests/permissions.py
    $ pmt apps.teams.tests.permissions

    # Tests defined as a class in apps/teams/tests/permissions.py
    $ pmt apps.teams.tests.permissions:TestRules

    # One specific test
    $ pmt apps.teams.tests.permissions:TestRules.test_can_add_video

    # Everything:
    $ pmt

Note: you may need to rebuild the Solr schema after running tests.  To do so,
run the following command on the server:

    sudo ./deploy/update_solr_schema_vagrant.sh

**TODO:** Fix this.

Optional
--------

You can optionally set up a few other pieces of the development environment that
we haven't automated yet.

### RabbitMQ and Celery

Add the following to `settings_local.py` to use RabbitMQ and Celery for async
tasks:

    CELERY_ALWAYS_EAGER = False
    CELERY_RESULT_BACKEND = "amqp"
    BROKER_BACKEND = 'amqplib'
    BROKER_HOST = "localhost"
    BROKER_PORT = 5672
    BROKER_USER = "usrmquser"
    BROKER_PASSWORD = "usrmqpassword"
    BROKER_VHOST = "ushost"

### Werkzeug Debugger

If you want to use the awesome Werkzeug debugging runserver instead of the
standard Django one, you just have to run (while the virtualenv is activated):

    pip install werkzeug

And then use `./dev-runserver.sh plus` to run it.

### bpython shell

If you want to use the awesome bpython shell instead of the normal one you just
need to run (while the virtualenv is activated):

    pip install bpython

Now when you run `pm shell` it will use bpython automatically.
