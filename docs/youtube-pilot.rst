Youtube pilot details
=====================

Sync rules
----------

Each of the environments should have a single instance of ``YoutubeSyncRule``
in the database.  This allows us to specify which Youtube videos should be
synced back to Youtube when edits are made.

There are three fields that you can use to set up your rules: *team*, *user*
and *video*.  Each of these fields will contain a comma-separated list of items
that should be synced.  If a video doesn't match any of the rules, it's simply
ignored and nothing special happens.


*team* should be a comma-separated list of team slugs that you want to sync.
*user* should be a comma-separated list of usernames of users whose videos
should be synced.  *video* is a list of primary keys of videos that should be
synced.

You can also specify a wildcard ``*`` (asterisk) to any of the above to match any teams,
any users, or any videos.

Configuration
-------------

In order to enable the Youtube pilot in an environment, there are a few things
that need to be configured first.

* The ``YoutubeSyncRule`` table has to be in the database.  There is a
  South migration provided to help with this.

* Set the ``YOUTUBE_ALWAYS_PUSH_USERNAME`` setting.  Our testing username is
  ``amarasubtitletest``.  Make sure that this Youtube account is linked to
  Amara via OAuth.  If the OAuth credentials are missing, we raise an
  ``ImproperlyConfigured`` exception.

* Make sure all the Youtube-related settings are populated:
  ``YOUTUBE_CLIENT_ID``, ``YOUTUBE_CLIENT_SECRET``, ``YOUTUBE_API_SECRET``
