==================
Api2 Documentation
==================

This is the documentation of v2 of Universal Subtitle's API. 

The v1 of the API is deprecated, but can still be accessed through http://www.universalsubtitles.org/api/1.0/documentation/ . Users should migrate to the v2 of the API. If you're missing a feature on the api, please `let us know <https://universalsubtitles.tenderapp.com/>`_ .


Authentication
===============
Before interacting with the api, you must have an API key. In order to get one, create a user on the Universal Subtitles website, then go to the `edit profile <http://www.universalsubtitles.org/en/profiles/edit/>`_ page. At the bottom of the page you will find a "Generate new key" button . Clicking on it will fetch your user the needed API key.

Every request must have the username and the api keys as headers. Ex::
   
   X-api-username: my_username_here
   X-apikey: my_api_key_here

Data Formats
=============
The api accepts request data and will output the following formats: JSON, XML and YAML. Unless you have a strong reason not to, we recommend using the JSON format, as it's the one that gets the most usage (and therefore more testing).

To specify the format, add the `Accept` header appropriately, ex::

    Accept: application/json

You can also specify the desired format in the url, sending the request variable `format=json`.

API ENDPOINT
=============

The endpoint for the api is the environment base URL +  `/api2/partners/`. Possible environments:

* Staging: https://staging.unversalsubtitles.org/ 
* Production: https://www.unversalsubtitles.org/

Therefore, most clients should be making requests againgst:
https://www.unversalsubtitles.org/api2/partners/

If you're under a partnership, you might have a different base URL. Please contact us if you're not sure.

Available Resources
===================

The following resources are available to end users:

VideoResource
==============

Represents a video on Universal Subtitles.

* Listing videos

  * Ex.

   GET https://www.unversalsubtitles.org/api2/partners/videos/

  * Parameters:
   
      * `video_url`: list only videos with the given URL, useful for finding out information about a video already on Universal Subtitles.
      * `order_by`: Applies sorting to the video list. Possible values:

          * `title`: ascending
          * `-title`: descending
          * `created`: older videos first
          * `-created` : newer videos
* Creating Videos:

  * Send a POST request::
  
   POST https://www.unversalsubtitles.org/api2/partners/videos/
   
   * Parameters:
       * `video_url` : The url for the video. Any url that Universal Subtitles accepts will work here. You can send the URL for a file (e.g. http:///www.example.com/my-video.ogv) , or a link to one of our accepted providers (youtube, vimeo, dailymotion, blip.tv)
       * `title` : The title for the video
       * `description` : About this video
       * `duration` : Duration in seconds
       * When submitting URLs of external providers (i.e. youtube, vimeo), the metadata (title, description, duration) can be fetched from them. If you're submitting a link to a file (mp4, flv) then you can make sure those attributes are set with these parameters. Note that these parameters do override any information from the original provider.
       
* Video Detail
Information about a specific video can be retrieved from the URL::

   GET https://www.unversalsubtitles.org/api2/partners/videos/[video-id]

The video listing resource already returns a `resource_uri` for each video to be used when retrieving the details.
