Youtube pilot details
=====================

How it works
------------

When a user edits subtitles for a Youtube video, we try to push those subtitles
to Youtube.  In contrast to the legacy system, we push subtitles for every
video regardless of whether the user has linked a third party account.

When we interact with the Youtube API to perform the syncing, we log in as the
``amarasubtitletest`` Youtube user.  This account has been set up for us by
Google and has some special attributes applied to it.  In order to make
authenticated requests, we need to go through the OAuth dance first.  The
current third party account linking process does just that so we use it to
produce and store the required OAuth tokens in the database.  If a
``ThirdPartyAccount`` instance can't be found for the ``amarasubtitletest``
username, we just skip the whole process.

Once the OAuth credentials are in place we need to set up a Youtube sync rule.
This allows us to specify which videos should be synced during testing.

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
should be synced.  *video* is a list of video ids of videos that should be
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
