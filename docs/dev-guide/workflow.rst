Development Workflow
====================

This guide describes the development workflow for Amara.

.. contents::

Branches
--------

The ``production`` branch is what gets deployed to our production server.
It's what gets deployed to production server.  ``staging`` branch
is what gets deployed to the staging server.  Commits should *never* be made
directly to production and only trivial commits should be made to staging.

Instead, Amara development tries to follow a "one branch per feature or
bugfix" workflow.  Typically changes happen like this:

  - Someone creates a github issue that captures the bug/feature
  - A developer creates a branch to handle the issue.  Each feature branch
    should be named after its issue number (e.g.  ``gh-1234`` would be a branch
    for github issue 1234).  Changes for the issue always get commited to this
    branch.
  - Once development on the issue is complete, we open a pull request from the
    topic branch to staging.  Another developer will review the code and merge
    it once they think it's good to go.
  - Once we decide that staging is ready to be deployed to production, we will
    merge the staging branch to production then deploy.

Creating issues
---------------

Please follow these guidelines when creating issues, to ensure that they are
easy to implement:

  - Do a quick search to check for any existing issues before creating a new
    one.
  - Make sure the title clearly and succinctly captures the issue at hand
  - For bugs, describe the steps needed to reproduce the problem and what
    the correct behavior is.
  - Try to describe the severity of the issue.  Who is it affecting?  How bad
    is the current behavior, etc.

Development Workflow
--------------------

Overview
~~~~~~~~

We use zenhub for project management.  It's basically a chrome extension that
adds a kanban-like board to github.  You can get it from
https://www.zenhub.com/.

Zenhub adds a pipeline field to github issues.  We use this field to track the
current status of work on the issue.  We use the following pipelines:

  - ``To Do`` -- Issue that a developer wants to work on, but hasn't started yet
  - ``In Progress`` -- Issue that a developer is currently working on
  - ``Testing`` -- Issue that a developer believes to be handled and needs
    testing to verify the fix
  - ``Waiting for Deploy`` -- Issue that has been fixed in the staging branch
    and we need to deploy the change to production.

Here's the workflow for a typical issue:

  - Someone creates a github issue to capture a bug/feature
  - Developer starts working on the issue.

     - They assign it to themself
     - Move the issue to the ``In progress`` pipeline
     - Create a topic branch to work in

  - Developer does the initial work on the feature

    - They commit code to the branch to handle the issue
    - Move the issue to the ``Testing`` pipeline
    - Add a comment to the github issue with any notes needed to test the
      issue (what changes were needed, any areas that should be thoroughly
      tested, etc.)

  - Tester tests the changes.  If there are problems they make a comment in
    the issue explaining them, then move it back to the ``In progress``
    pieline.  As work continues, we iterate back and forth between ``In
    progress`` and ``Testing``.
  - Once the tester decides everyting is set to go, they:

    - Create a pull request in github from the topic branch to staging
    - Add a comment explaining any notes that came up during testing

  - A second developer reviews the code.

    - If there are any issues, they should add a comment to the pull request
      and the first developer should address them.
    - Once the code is good, then we merge to staging.
    - Once the code is merged, the tester should move the issue to the
      ``Waiting for deploy`` pipeline

  - At some point we decide to deploy the code on staging to production.

     - When this happens the tester closes the issue.

Keep the Topic Branch Up To Date
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As you work on your topic branch, other branches may have been merged into
``staging`` by other people.  Make sure you merge staging back to your branch
as often as possible to keep it up-to-date.

Testing
~~~~~~~

At a minimum, make sure you :ref:`run the tests <running-tests>`
after your changes and ensure that all tests pass.

If possible, use test driven development.  Write new tests that cover the
issue you're working on before you start any code.  Write code that makes the
test pass.  Then consider refactoring code to fix the problem in a cleaner
way.

Other Git Repositories
----------------------

Inside the unisubs repository, you may want to check out some other repositories.

If you have access to our private repository
(https://github.com/pculture/amara-enterprise/).  Check that out inside the
root directory of the unisubs repository to add the extra functionality.  See
:ref:`optional-apps` for details on how this works.

We also have a couple other repositories that integrate into unisubs:

  - https://github.com/pculture/babelsubs/
  - https://github.com/pculture/unilangs/

Both of these get installed inside your docker container.  Normally you don't
need to do anything to use them.  However, if you want to test changes to
those repositories you need to check out a local copy:

  - Check out the git repository inside the root unisubs directory.
  - Make a symlink from the root directory to the python package (for example:
    ``ln -s babelsubs-git/babelsubs .``)
  - After this the unisubs code will be using your local checkout rather than
    the default package.  Make changes there, test them on your dev
    environment, then commit/push the changes back to a branch on the pculture
    repository, then open a PR to maste.
  - When we deploy amara, we pick up the the latest commit in master for these
    libraries.  So once your changes are merged to master, they will be live
    the next time we deploy.
