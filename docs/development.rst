Development Guide
=================

This guide describes the development workflow for Amara.

.. contents::

Git Setup
---------

TODO: Write a git precommit hook and describe how to install it.

Branches
--------

Amara development tries to follow a "one branch per feature or bugfix" workflow
(for the most part).  There are two main parts.

First, the ``master`` branch is the "base" branch.  It's what gets deployed to
staging and production servers.  Commits should *never* be made directly on this
base branch (except for merges).

Actual code changes should *always* be made on "feature" branches.  Each feature
branch should contain changes related to a single feature or bugfix.  Each
feature or bugfix should have an issue in the bug tracker (Sifter).  Each
feature branch should be named after its issue number (e.g.  ``i-1234`` would be
a branch for issue 1234).

Workflow
--------

The Amara development workflow should go something like this.

Create an Issue
~~~~~~~~~~~~~~~

First, a Sifter issue is created for the task.  It might be a new feature, a bug
fix, or some code cleanup.  For this example we'll assume the issue number is
1234.

Create a Feature Branch
~~~~~~~~~~~~~~~~~~~~~~~

A Git branch for the issue is created from the current head of ``master``, and
it is named ``i-1234``.

Create an Instance
~~~~~~~~~~~~~~~~~~

To test changes non-locally an instance will need to be created for the feature
branch.  You should do this as soon as you create the branch, so that test data
will be populated (and later migrated) correctly.

Create the "demo" instance using either Launchpad (https://launchpad.amara.org)
or Fabric.

Using Launchpad, login and select the "Create Demo from Branch"
workflow.  Select the branch from the dropdown and an optional url.  You will
need to enter the full url name: (i.e. ``mybranch.demo.amara.org``). If you
don't specify a custom url, the branch name will be used.

If you use fabric, use the following:

``fab demo:<username>,<branch_name> create_demo``

Or to use a custom url:

``fab demo:<username>,<branch_name> create_demo:url_prefix=mybranch.demo.amara.org``

Make Changes on the Feature Branch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Changes that fulfill the issue are made on that branch.  The repository now
looks like this::

    .
      O i-1234
      |
      O
     /
    O master
    |

Commit messages should start with the issue number, a colon, and a space, like
this::

    1234: Remove the foo from the bar

This makes it easy to grep the Git log for changes related to a specific issue.

If at all possible, the developer should add a test case that covers the
feature/bug as a separate commit first.

They can then push that to the branch on GitHub, watch it fail, then add the
code that fixes the problem and watch it start passing.  This is a good sanity
check that their code (and test) does what they think it does.

Keep the Feature Branch Up To Date
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As the programmer works on the feature branch, other feature branches may have
been merged into ``master`` by other people.  The programmer should merge these
changes back into their feature branch as often as possible to keep it up to
date.  For example::

    .
                  master O
                        /|
                       | | O i-1234
       work by another . | |
    dev on a different . | |
        feature branch . | |
                       | | O
                        \|/
                         O
                         |

The programmer working on ``i-1234`` should merge these changes into their
feature branch to keep it up to date::

    .
                           O i-1234
                          /|
                  master O |
                        /| |
                       | | O 
       work by another . | |
    dev on a different . | |
        feature branch . | |
                       | | O
                        \|/
                         O
                         |

Run the Full Test Suite
~~~~~~~~~~~~~~~~~~~~~~~

The small set of tests should be run automatically after every commit.  Once the
programmer thinks they've solved the issue they should kick off the full suite
of Selenium tests and wait for the results (by email).

TODO: Describe how to do this.

Resolve the Ticket for QA
~~~~~~~~~~~~~~~~~~~~~~~~~

Along with the automated test suite which should be run automatically, QA will
need to test the changes.  Once the developer has received the full tests
results (and they're passing) they should resolve the Sifter ticket.  QA will
then test the instance running from the ``i-1234`` branch.

If there's a problem, they'll reopen the ticket and the developer can make some
more changes on the feature branch.  Otherwise they'll comment on the ticket and
say that it's ready to go.

Merging Back to the Base Branch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once QA has tested a feature branch, the developer should send a pull request
to merge ``i-1234`` back into ``master``.  The other developers should review
all the code as a last line of defense against bugs.

If there's a problem, the original developer should make some more changes on
``i-1234`` that fix the problem, QA retests, and a new pull request should be
made.

Otherwise, the branch can be merged into ``master``.

Delete the Feature Branch
~~~~~~~~~~~~~~~~~~~~~~~~~

Once the feature branch (``i-1234``) has been merged back into the base branch
(``master``) it can be deleted.

You can find commits made on a particular feature branch later by grepping
through the commit logs for ``1234:``, thanks to the commit message format.

The git command to delete a branch both locally and remotely is:

::

    git push origing --delete i-1234

Delete the Instance
~~~~~~~~~~~~~~~~~~~

From the launchpad, choose `Delete Demo` and remove it.  If you use fabric, use
the following:

::

    fab demo:<username>,<branch_name> remove_demo

Deploy to Production
~~~~~~~~~~~~~~~~~~~~

Once the feature branch has been merged back into the base branch and deleted,
the base branch can be deployed to production.

TODO: Have Evan describe how to do this.

Integration Repository
----------------------

The integration repository should function the same way as the main repository.

If you don't need to make any changes inside of it there's no need to create
an empty ``i-####`` feature branch in it though.

TODO: Add more details here.

"Buffer" Branches
-----------------

Sometimes there are larger projects that span multiple Sifter issues which don't
make sense to deploy individually.  When this is the case, a "buffer" branch
should be used.

A "buffer" branch is a separate Git branch with a descriptive name like
``data-model-refactor`` or ``new-editor``.  Once created it takes over the role
of the "base" branch for changes related to that project.

Instead of creating ``i-2222`` as a branch off of ``master``, it would be
created as a branch off of ``new-editor``.  It would be kept up to date by
merging ``new-editor`` back in, and once complete a pull request to merge it
back into ``new-editor`` would be created.

Note that ``new-editor`` itself should be kept up to date with changes from
``master`` as well.

An instance can be deployed to track the buffer branch itself (in addition to
instances for each feature branch off of it).

Once all the development has been completed, the buffer branch itself can be
merged back into ``master`` and deployed.

Basic Example
-------------

Let's walk through a full example of a workflow.  First, we'll start with
a clean slate::

    .

    O master
    |
    ⋯

Now someone creates a feature branch for an issue and makes some changes::

    .

      O i-1111
      |
      O
     /
    O master
    |
    ⋯

At the same time, someone *else* creates a feature branch for a different
issue::

    .

    i-2222 O
           |
           |   O i-1111
           |   |
           |   O
            \ /
             O master
             |
             ⋯

Now the first developer marks their ticket as resolved, QA tests, and everything
is okay.

They create a pull request to merge ``i-1111`` back into ``master``.  The other
developers review it and it looks fine, so they merge it and delete the feature
branch::

    .

             O master
    i-2222 O |\
           | | |
           | | O
           | | |
           | | O
            \|/
             O
             |
             ⋯

Now the second developer notices that there are new changes on ``master``, so
they merge ``master`` into their feature branch to keep the feature branch up to
date::

    .

    i-2222 O
           |\
           | O master
           O |\
           | | |
           | | O
           | | |
           | | O
            \|/
             O
             |
             ⋯

They make a few more changes::

    .

    i-2222 O
           |
           O
           |
           O
           |\
           | O master
           O |\
           | | |
           | | O
           | | |
           | | O
            \|/
             O
             |
             ⋯

They mark the ticket as resolved, QA tests, they create a pull request, devs
review, and their feature branch gets merged into ``master`` and deleted::

    .

             O master
            /|
           O |
           | |
           O |
           | |
           O |
           |\|
           | O
           O |\
           | | |
           | | O
           | | |
           | | O
            \|/
             O
             |
             ⋯

Buffer Branch Example
---------------------

TODO: This.
