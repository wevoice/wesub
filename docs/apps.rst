Django apps
===========

Here is a list of pluggable Django apps that Amara is using.  All
of these apps are contained in the ``apps/`` directory.

.. warning:: The ``apps/`` directory is added to the Python path so you can
    import it directly.  ``from videos.models import Video`` is prefered over
    ``from apps.vides.models import Video``.

* account linker
    Amara allows you to publish your finished subtitles back to
    YouTube via their API.  This app handles that.

* auth
    This app contains a custom ``User`` model and authentication business
    logic.

* comments
    Comments on videos and subtitles

* icanhaz
    Private video management: can you see this video?

* localeurl
    This app adds ``/en/`` to the url.  It makes sure that the correct
    translation is being shown.

* messages
    in-app inbox, notifications

* openid consumer

* profiles
    User profile, settings, dashboard

* search
    Full text search on videos; List of most popular videos

* socialauth
    Social media integration (Twitter, Facebook)

* statistics
    View counts

* streamer
    Rendering subtitles in HTML

* teams
    Team workflows, permissions

* test helpers

* unisubs compressor
    Custom static file compressor

* uslogging
    Amara logging, errors on widgets

* videos
    Transcription, translation, video management

* widget
    Embedded widget
