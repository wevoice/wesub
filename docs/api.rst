API Documentation
=================

This is the documentation of v2 of Amara's API. Please contact us
if you’d like to use the Amara API for commercial purposes.

.. note:: The v1 of the API is deprecated, but can still be accessed through
    http://www.universalsubtitles.org/api/1.0/documentation/ . Users should migrate
    to the v2 of the API. If you're missing a feature on the API, please `let us
    know <https://universalsubtitles.tenderapp.com/>`_ .

Authentication
--------------

Before interacting with the API, you must have an API key. In order to get one,
create a user on the Amara website, then go to the `edit profile
<http://www.universalsubtitles.org/en/profiles/edit/>`_ page. At the bottom of
the page you will find a "Generate new key" button . Clicking on it will fetch
your user the needed API key.

Every request must have the username and the API keys as headers. For example::

   X-api-username: my_username_here
   X-apikey: my_api_key_here

So a sample request would look like this::

   $ curl  -H 'X-api-username: site_username' -H 'X-apikey: the_apy_key' \
    https://staging.universalsubtitles.org/api2/partners/videos/

Data Formats
------------

The API accepts request data and will output the following formats: JSON, XML
and YAML. Unless you have a strong reason not to, we recommend using the JSON
format, as it's the one that gets the most usage (and therefore more testing).

To specify the format, add the ``Accept`` header appropriately, for example::

    Accept: application/json

You can also specify the desired format in the url, sending the request
variable ``format=json``.

API endpoint
------------

The endpoint for the API is the environment base URL +  ``/api2/partners/``.

Possible environments:

* Staging: ``https://staging.universalsubtitles.org/``
* Production: ``https://www.universalsubtitles.org/``

Therefore, most clients should be making requests against:
``https://www.universalsubtitles.org/api2/partners/``

All API requests should go through https. The staging environment might need
HTTP basic auth, please contact us to request credentials.  When basic auth is
needed on staging, you end up with a request like this::

    $ curl  -H 'X-api-username: site_username' -H 'X-apikey: the_apy_key' \
        --user basic_auth_username:basic_auth_password \
        https://staging.universalsubtitles.org/api2/partners/videos/

If you're under a partnership, you might have a different base URL. Please
contact us if you're not sure.

Available Resources
-------------------

All resources share a common structure when it comes to the basic data
operations.

* ``GET`` request is used to viewing data
* ``POST`` request is used for creating new items
* ``PUT`` request is used for updating existing items
* ``DELETE`` request is used for deleting existing items

For example, in order to request a list of teams the user is current on, you
would issue the following request:

.. http:get:: /api2/partners/teams/

To view a detail of the ``test`` team, you could do:

.. http:get:: /api2/partners/teams/test/

    Example response

    .. sourcecode:: http

        {
            "created": "2012-04-18T09:26:59",
            "deleted": false,
            "description": "",
            "header_html_text": "",
            "is_moderated: false",
            "is_visible: true",
            "logo: null",
            "max_tasks_per_member": null,
            "membership_policy: ""Open",
            "name: "test","
            "projects_enabled": false,
            "resource_uri: "/"api2/partners/teams/test/",
            "slug: "test","
            "subtitle_policy": "Anyone",
            "task_assign_policy": "Any team member",
            "task_expiration: null",
            "translate_policy: "Anyone"",
            "video_policy: "Any team member",
            "workflow_enabled": false
        }

Here is an example of creating a new team via ``curl``.

.. code-block:: bash

    curl -i -X POST -H "Accept: application/json" \
        -H "X-api-username: username" -H "X-apikey: your-api-key" \
        -H "Content-Type: application/json" \
        --data '{"name": "Team name", "slug": "team-name"}' \
        http://host/api2/partners/teams/

You can use the same fields that you get back when requesting a team detail.

To update a team, you could issue a request like this:

.. code-block:: bash

    curl -i -X PUT -H "Accept: application/json" \
        -H "X-api-username: username" -H "X-apikey: your-api-key" \
        -H "Content-Type: application/json" \
        --data '{"name": "My team name"}' \
        https://host/api2/partners/teams/test/

The following resources are available to end users:

Video Resource
~~~~~~~~~~~~~~

Represents a video on Amara.

Listing videos

.. http:get:: /api2/partners/videos/

    :query video_url:  list only videos with the given URL, useful for finding out information about a video already on Amara.
    :query team:       Only show videos that belong to a team identified by ``slug``.
    :query project:    Only show videos that belong to a project with the given slug.
        Passing in ``null`` will return only videos that don't belong to a project.
    :query order_by:   Applies sorting to the video list. Possible values:

        * `title`: ascending
        * `-title`: descending
        * `created`: older videos first
        * `-created` : newer videos

Creating Videos:

.. http:post:: /api2/partners/videos/

    :form video_url: The url for the video. Any url that Amara accepts will work here. You can send the URL for a file (e.g. http:///www.example.com/my-video.ogv) , or a link to one of our accepted providers (youtube, vimeo, dailymotion, blip.tv)
    :form title: The title for the video
    :form description: About this video
    :form duration: Duration in seconds

When submitting URLs of external providers (i.e. youtube, vimeo), the metadata
(title, description, duration) can be fetched from them. If you're submitting a
link to a file (mp4, flv) then you can make sure those attributes are set with
these parameters. Note that these parameters do override any information from
the original provider.

Information about a specific video can be retrieved from the URL:

Video Detail:

.. http:get:: /api2/partners/videos/[video-id]/

The video listing resource already returns a ``resource_uri`` for each video to
be used when retrieving the details.

Updating a video object:

.. http:put:: /api2/partners/videos/[video-id]/

With the same parameters for creation. Note that through out our system, a
video cannot have it's URLs changed. So you can change other video attributes
(title, description) but the URL sent must be the same original one.

Moving videos between teams
+++++++++++++++++++++++++++

In order to move a video from one team to another, you can make a request to
change the video where you change the ``team`` value in the Video Resource.

In order to move the video from *Team A* to *Team B*, you would make the
following request.

.. code-block:: bash

    curl -i -X PUT -H "Accept: application/json" \
        -H "X-api-username: username" -H "X-apikey: your-api-key" \
        -H "Content-Type: application/json" \
        --data '{"team": "team_b"}' \
        https://host/api2/partners/videos/video-id/

Please note that the value that is sent as the ``team`` is the team's slug.
The user making the change must have permission to remove a video from the
originating team and permission to add a video to the target team.

Setting the ``team`` value to ``null`` will remove it from its current team.

A similar mechanism can be used to change what project a given video is filed
under.

Video Language Resource
~~~~~~~~~~~~~~~~~~~~~~~

Represents a language for a given video on Amara.

Listing video languages:

.. http:get:: /api2/partners/videos/[video-id]/languages/

Creating Video Languages:

.. http:post:: /api2/partners/videos/[video-id]/languages/

    :form language_code: The language code (e.g 'en' or 'pt-br') to create. 
    :form title: The title for the video localized to this language - optional
    :form description: Localized description for this language - optional.
    :form is_original: Boolean indicating if this is the original language for the video. - optional - defaults to false.
    :form is_complete: Boolean indicating if the complete subtitling set is available for this language - optional, defaults to false.

.. seealso::  To list available languages, see ``Language Resource``.

Information about a specific video language can be retrieved from the URL:

.. http:get:: /api2/partners/videos/[video-id]/languages/[lang-identifier]/

    :param lang-identifier: language identifier can be the language code (e.g. ``en``) or the
        numeric ID returned from calls to listing languages.

Subtitles Resource
~~~~~~~~~~~~~~~~~~

Represents the subtitle set for a given video language.

Fetching subtitles for a given language:

.. http:get:: /api2/partners/videos/[video-id]/languages/[lang-identifier]/subtitles/?format=srt
.. http:get:: /api2/partners/videos/asfssd/languages/en/subtitles/?format=dfxp
.. http:get:: /api2/partners/videos/asfssd/languages/111111/subtitles/?format=ssa

    :query format: The format to return the subtitles in. Supports all the
        formats the regular website does: rst, ssa, txt, dfxp, ttml.
    :query version: the numeric version number to fetch.  Versions are listed in the
        VideoLanguageResouce request.

If no version is specified, the latest public version will be returned. For
videos that are not under moderation it will be the latest one. For videos
under moderation only the latest published version is returned. If no version
has been accepted in review, no subtitles will be returned.

Creating new subtitles for a language:

.. http:post:: /api2/partners/videos/[video-id]/languages/[lang-identifier]/subtitles/
.. http:post:: /api2/partners/videos/asfssd/languages/en/subtitles/

    :query subtitles: The subtitles to submit
    :query sub_format: The format used to parse the subs. The same formats as
        for fetching subtitles are accepted. Optional - defaults to ``srt``.

This will create a new subtitle version with the new subtitles.


Language Resource
~~~~~~~~~~~~~~~~~

Represents a listing of all available languages on the Amara
platform.

Listing available languages:

.. http:get:: /api2/partners/languages/

User Resource
~~~~~~~~~~~~~

One can list and create new users through the API.

Listing users:

.. http:get:: /api2/partners/users/

User datail:

.. http:get:: /api2/partners/users/[username]/

Creating Users:

.. http:post:: /api2/partners/users/

    :form username: the username for later login.  30 chars or fewer alphanumeric chars, @, _ and - are accepted.
    :form email: A valid email address
    :form password: any number of chars, all chars allowed.
    :form first_name: Any chars, max 30 chars. Optional.
    :form last_name: Any chars, max 30 chars. Optional.
    :form create_login_token: If sent the response will also include a url that when clicked will login the recently created user. This URL expires in 2 hours

The response also includes the 'api_key' for that user. If clients wish to make
requests on behalf of this newly created user through the api, they must hold
on to this key, since it won't be returned in the detailed view.

Video Url Resource
~~~~~~~~~~~~~~~~~~

One can list, update, delete and add new video urls to an existing video.

Listing video urls

.. http:get:: /api2/partners/videos/[video-id]/urls/

Video URL detail:

.. http:get:: /api2/partners/users/[video-id]/urls/[url-id]/

Where the url-id can be fetched from the list of urls.

Updating video-urls:

.. http:put:: /api2/partners/users/[video-id]/urls/[url-id]/

Creating video-urls:

.. http:post:: /api2/partners/users/[video-id]/urls/

    :form url: Any URL that works for the regular site (mp4 files, youtube, vimeo,
        etc) can be used. Note that the url cannot be in use by another video.
    :form primary:  A boolean. If true this is the url the will be displayed first
        if multiple are presents. A video must have one primary URL. If you add /
        change the primary status of a url, all other urls for that video will have
        primary set to false. If this is the only url present it will always be set
        to true.
    :form original: If this is the first url for the video.

To delete a url:

.. http:delete:: /api2/partners/users/[video-id]/urls/[url-id]/

If this is the only URL for a video, the request will fail. A video must have
at least one URL.

Team Resource
~~~~~~~~~~~~~

You can list existing teams:

.. http:get:: /api2/partners/teams/

You can view details for an existing team:

.. http:get:: /api2/partners/teams/[team-slug]/

Creating a team:

.. http:post:: /api2/partners/teams/

Updating a team:

.. http:put:: /api2/partners/teams/[team-slug]/

Deleting a team:

.. http:delete:: /api2/partners/teams/[team-slug]/

.. note:: You can only create new teams if you have been granted this
    privilege.  Contact us if you require a partner account.

Policy values
+++++++++++++

Membership policy:

* ``Open``
* ``Application``
* ``Invitation by any team member``
* ``Invitation by manager``
* ``Invitation by admin``

Video policy:

* ``Any team member``
* ``Managers and admins``
* ``Admins only``

Task assign policy:

* ``Anyone``
* ``Any team member``
* ``Only managers and admins``
* ``Only admins``

Project Resource
~~~~~~~~~~~~~~~~

List all projects for a given team:

.. http:get:: /api2/partners/teams/[team-slug]/projects/

Project detail:

.. http:get:: /api2/partners/teams/[team-slug]/projects/[project-slug]/

Create a new project:

.. http:post:: /api2/partners/teams/[team-slug]/projects/

Example payload for creating a new project:

::

    {
        "name": "Project name",
        "slug": "project-slug",
        "description": "This is an example project.",
        "guidelines": "Only post family-friendly videos."
    }

.. note:: You can only create projects for a specific team.

Update an existing project:

.. http:put:: /api2/partners/teams/[team-slug]/projects/[project-slug]/

For example, to change the project's name:

::

    {
        "name": "Project"
    }

Delete a project:

.. http:delete:: /api2/partners/teams/[team-slug]/projects/[project-slug]/