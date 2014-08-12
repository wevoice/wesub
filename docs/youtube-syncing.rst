Youtube syncing
===============

Most of the Youtube syncing logic is contained in three places:

* ``videos.types.youtube``
* ``videos.tasks.add_amara_description_credit_to_youtube_video``
* ``accountlinker.models``

The central place for Youtube API interaction is the
``video.types.youtube.YouTubeAPIBridge`` class.

Latest work was done on the **staging** branch (as opposed to **dev**).

What we do
----------

Here is a list of things that we do when we interact with the Youtube API:

* Import Youtube videos (one-off and periodical)
* Import subtitles from Youtube videos
* Push Amara subtitles to Youtube
* Add Amara credit to Youtube video descriptions
* Add Amara credit as the last subtitle of a Youtube video's language
* OAuth authorization

How linking works
-----------------

Whenever a user links their Youtube account to Amara, we add their feed to the
system so that all existing videos are added to Amara immediately and any
future videos are added automatically.  When a user unlinks their Youtube
account, we should remove the feed as well.

Whenever any Youtube video is added to Amara outside of a team context we
should check if the video's Youtube owner has a linked account on Amara.  If
so, we should immediately add the Amara link to the video's description on
Youtube. 

Videos that were submitted to Amara by a user other than the account owner
should also sync subtitles to youtube if the account owner has their account
linked.

Syncing
-------

Subtitles are only synced to youtube when the video language is marked 
'complete' and the subtitles are 'public'.

If a complete and public language is edited and marked incomplete - 
the subtitles remain unchanged on youtube.  If the language is later marked
as complete, the subtitles are synced.

Credits
-------

Credits should be localized based on the video language or the subtitle
language.

Subtitle credits are inserted into the last three seconds of the video.  If
there is less than 3 seconds left, we take up whatever space there is.

The description credit is inserted above the existing video description.  There
is a ``remove_youtube_credit`` management command that can be used to fix a
video that had the credit applied by accident.

API quota issues
----------------

We have had some issues with rate limiting.  If we make too many calls within
a short period of time, we get blocked for a few minutes.  We seem to be able
to make an unlimited amount of calls as long as they are spaced out.

To give you an idea how much we can do, importing a video feed with 100 videos
will only import about 60 videos before choking.

Currently, we raise a ``videos.types.youtube.TooManyRecentCallsException`` when
we hit the quota error.

We are working with someone from the Youtube API support team to resolve this
issue.

Working around quota issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a few things we can do based on our understanding of the problem.

*  Create a dedicated celery queue for Youtube-related tasks
*  Create a second celery worker machine to spread all tasks over 2 IP
   addresses
*  Rate limit the queue to one task execution per second (`Celery
   documentation on rate limiting`_)
*  Set a ``yt:quota_exceeded`` key in Redis if we're over limit
*  Retry task in 90 seconds if we are over limit (`Retrying example`_)

It would also help if we alterned users on whose behalf we make the API
request.  Instead of doing 5 requests as user A and then 5 requests as user B,
it would be better to alternate: A1, B1, A2, B2, etc.  Looking for suggestions
on how to do implement that.

.. _Celery documentation on rate limiting: http://docs.celeryproject.org/en/latest/userguide/tasks.html#Task.rate_limit
.. _Retrying example: http://docs.celeryproject.org/en/latest/userguide/tasks.html#retrying>

Alternating users architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.  All Youtube API celery tasks will be packaged into a dict and sent to a
    ``waiting`` queue.  The dict will contain the task name, arguments and user
    information.

2.  At the end of the ``waiting`` queue is a single concurrency worker that
    will pop off a batch of tasks and sort them into lists by user.  It will
    then take those lists and round robbin sort them.  Once sorted, it will
    queue those tasks on the ``youtube`` queue.

3.  At the end of the ``youtube`` queue is one or more single concurrency
    workers making requests to the Youtube API.  Each of these workers should
    be on a separate machine with a different IP.

Metrics
-------

You can have a look at the rates in Graphite.  All of the Youtube stuff is
namespaced under ``youtube``.  Things that we currently measure:

* API calls
* Descriptions changed
* Languages imported
* Subtitles pushed
* Videos imported
* Too many recent calls exception thrown (occurrence)
