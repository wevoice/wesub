API Documentation
=================

This is the documentation of v2 of Amara's API. Please contact us
if you’d like to use the Amara API for commercial purposes.

The v1 of the API is deprecated, but can still be accessed through http://www.universalsubtitles.org/api/1.0/documentation/ . Users should migrate to the v2 of the API. If you're missing a feature on the api, please `let us know <https://universalsubtitles.tenderapp.com/>`_ .

Authentication
--------------

Before interacting with the api, you must have an API key. In order to get one,
create a user on the Amara website, then go to the `edit profile
<http://www.universalsubtitles.org/en/profiles/edit/>`_ page. At the bottom of
the page you will find a "Generate new key" button . Clicking on it will fetch
your user the needed API key.

Every request must have the username and the api keys as headers. For example::

   X-api-username: my_username_here
   X-apikey: my_api_key_here

So a sample request would look like this::

   $ curl  -H 'X-api-username: site_username' -H 'X-apikey: the_apy_key'  https://staging.universalsubtitles.org/api2/partners/videos/

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

The endpoint for the api is the environment base URL +  ``/api2/partners/``.

Possible environments:

* Staging: https://staging.universalsubtitles.org/
* Production: https://www.universalsubtitles.org/

Therefore, most clients should be making requests against:
https://www.universalsubtitles.org/api2/partners/

All API requests should go through https. The staging environment might need
HTTP basic auth, please contact us to request credentials.  When basic auth is
needed on staging, you end up with a request like this::

    $ curl  -H 'X-api-username: site_username' -H 'X-apikey: the_apy_key' --user basic_auth_username:basic_auth_password https://staging.universalsubtitles.org/api2/partners/videos/

If you're under a partnership, you might have a different base URL. Please
contact us if you're not sure.

Available Resources
-------------------

The following resources are available to end users:

VideoResource
~~~~~~~~~~~~~

Represents a video on Amara.

Listing videos::

    GET https://www.universalsubtitles.org/api2/partners/videos/

Parameters:
    * `video_url`: list only videos with the given URL, useful for finding out information about a video already on Amara.
    * `order_by`: Applies sorting to the video list. Possible values:
    * `title`: ascending
    * `-title`: descending
    * `created`: older videos first
    * `-created` : newer videos
          
Creating Videos::
  
  POST https://www.universalsubtitles.org/api2/partners/videos/
   
Parameters:
  * `video_url` : The url for the video. Any url that Amara accepts will work here. You can send the URL for a file (e.g. http:///www.example.com/my-video.ogv) , or a link to one of our accepted providers (youtube, vimeo, dailymotion, blip.tv)
  * `title` : The title for the video
  * `description` : About this video
  * `duration` : Duration in seconds

When submitting URLs of external providers (i.e. youtube, vimeo), the metadata
(title, description, duration) can be fetched from them. If you're submitting a
link to a file (mp4, flv) then you can make sure those attributes are set with
these parameters. Note that these parameters do override any information from
the original provider.

Information about a specific video can be retrieved from the URL:

Video Detail::

  GET https://www.universalsubtitles.org/api2/partners/videos/[video-id]/

The video listing resource already returns a `resource_uri` for each video to
be used when retrieving the details.

Updating a video object::

   PUT https://www.universalsubtitles.org/api2/partners/videos/[video-id]/

With the same parameters for creation. Note that through out our system, a
video cannot have it's URLs changed. So you can change other video attributes
(title, description) but the URL sent must be the same original one.

VideoLanguageResource
~~~~~~~~~~~~~~~~~~~~~

Represents a language for a given video on Amara.

Listing video languages::

      GET https://www.universalsubtitles.org/api2/partners/videos/[video-id]/languages/

Creating Video Languages::

     POST https://www.universalsubtitles.org/api2/partners/videos/[video-id]/languages/

Parameters:
  * `language_code` : The language code (e.g 'en' or 'pt-br') to create. To list available languages, see `LanguageResource`
  * `title` : The title for the video localized to this language - optional
  * `description` : Localized description for this language - optional.
  * `is_original` : Boolean indicating if this is the original language for the video. - optional - defaults to false.
  * `is_complete` : Boolean indicating if the complete subtitling set is available for this language - optional, defaults to false.
  * TODO: implement language dependency (create a English version from French, for example)

Information about a specific video language can be retrieved from the URL::

   GET https://www.universalsubtitles.org/api2/partners/videos/[video-id]/languages/[lang-identifier]/

Where the language identifier can be the language code (e.g. 'en') or the
numeric ID returned from calls to listing languages.

SubtitlesResource
~~~~~~~~~~~~~~~~~

Represents the subtitle set for a given video language.

Fetching subtitles for a given language::

   GET https://www.universalsubtitles.org/api2/partners/videos/[video-id]/languages/[lang-identifier]/subtitles/?format=srt
   GET https://www.universalsubtitles.org/api2/partners/videos/asfssd/languages/en/subtitles/?format=dfxp
   GET https://www.universalsubtitles.org/api2/partners/videos/asfssd/languages/111111/subtitles/?format=ssa

Available parameters

   * `format`: The format to return the subtitles in. Supports all the formats the regular website does: rst, ssa, txt, dfxp, ttml.
   * `version`: the numeric version number to fetch.  Versions are listed in the VideoLanguageResouce request.

   If no version is specified, the latest public version will be returned. For videos that are not under moderation it will be the latest one. For videos under moderation only the latest published version is returned. If no version has been accepted in review, no subtitles will be returned.

Creating new subtitles for a language::

   POST  https://www.universalsubtitles.org/api2/partners/videos/[video-id]/languages/[lang-identifier]/subtitles/
   POST https://www.universalsubtitles.org/api2/partners/videos/asfssd/languages/en/subtitles/

Parameters:

   * `subtitles`: The subtitles to submit
   * `sub_format`: The format used to parse the subs. The same formats as for fetching subtitles are accepted. Optional - defaults to `srt`.

   This will create a new subtitle version with the new subtitles.


LanguageResource
~~~~~~~~~~~~~~~~

Represents a listing of all available languages on the Amara
platform.

Listing available languages::

   GET https://www.universalsubtitles.org/api2/partners/languages/

UserResource
~~~~~~~~~~~~

One can list and create new users through the API.

Listing users::

    GET https://www.universalsubtitles.org/api2/partners/users/

User datail::

    GET https://www.universalsubtitles.org/api2/partners/users/[username]/

Creating Users::

    POST https://www.universalsubtitles.org/api2/partners/users/

Parameters:

  * `username`: the username for later login.  30 chars or fewer alphanumeric chars, @, _ and - are accepted.
  * `email`: A valid email address
  * `password`: any number of chars, all chars allowed.
  * `first_name`: Any chars, max 30 chars. Optional.
  * `last_name`: Any chars, max 30 chars. Optional.
  * `create_login_token` : If sent the response will also include a url that when clicked will login the recently created user. This URL expires in 2 hours

The response also includes the 'api_key' for that user. If clients wish to make
requests on behalf of this newly created user through the api, they must hold
on to this key, since it won't be returned in the detailed view.

VideoUrlResource
~~~~~~~~~~~~~~~~

One can list, update, delete and add new video urls to an existing video.

Listing video urls::

    GET https://www.universalsubtitles.org/api2/partners/videos/[video-id]/urls/

Video URL detail::

    GET https://www.universalsubtitles.org/api2/partners/users/[video-id]/urls/[url-id]/

Where the url-id can be fetched from the list of urls.

Updating video-urls ::

    PUT https://www.universalsubtitles.org/api2/partners/users/[video-id]/urls/[url-id]/

Creating video-urls ::

    POST https://www.universalsubtitles.org/api2/partners/users/[video-id]/urls/


Parameters for creating or updating:

  * `url`: Any URL that works for the regular site (mp4 files, youtube, vimeo, etc) can be used. Note that the url cannot be in use by another video.
  * `primary`:  A boolean. If true this is the url the will be displayed first if multiple are presents. A video must have one primary URL. If you add / change the primary status of a url, all other urls for that video will have primary set to false. If this is the only url present it will always be set to true.
  * `original`: If this is the first url for the video.

To delete a url ::


    DELETE https://www.universalsubtitles.org/api2/partners/users/[video-id]/urls/[url-id]/

If this is the only URL for a video, the request will fail. A video must have
at least one URL.

TeamResource
~~~~~~~~~~~~

One can list existing teams:

::

    GET https://www.universalsubtitles.org/api2/partners/teams/

Once can view a detail for a team:

::

    GET https://www.universalsubtitles.org/api2/partners/teams/[team-slug]/


Example response:

::

    GET https://www.universalsubtitles.org/api2/partners/teams/test/

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

Creating teams
++++++++++++++

::

    POST https://www.universalsubtitles.org/api2/partners/teams/

For example

.. code-block:: bash

    curl -i -X POST -H "Accept: application/json" \
        -H "X-api-username: username" -H "X-apikey: your-api-key" \
        -H "Content-Type: application/json" \
        --data '{"name": "Team name", "slug": "team-name"}' \
        https://www.universalsubtitles.org/api2/partners/teams/

You can use the same fields that you get back when requesting a team detail.
