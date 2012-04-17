========================
HTTP Callbacks for Teams
========================

Enterprise customers can register an http callback so that any activity on their teams will fire an HTTP request. 

Customers can then decide on how to act upon those notifications, for example querying through the API to fetch a new set of subtitles.

To register your Team to receive HTTP notfications get in contact with us, this process is done manually, there is no UI for this over the website at the moment.

Pick one URL where you'd like to get notified. Each team can have their own URL, or a URL can be used amongst serveral teams (for example in a public / private team setup)

Optionally you can use basic HTTP auth over that URL. We recomend the URL uses https for safer communication (even though no passwords or sensitive data will ever be sent).

A HTTP POST request will be sent to the desired URL. Bellow a list of available signals and the data passed to them.


Available Data
==============
When a POST request is made to the chosen URL, the following data will be sent:

* `event_name` : A string, available events are: 

 * `video-new` : A new video has been added through the team (through the web ui)
 * `video-edited` : Video data has been edited (video url, title, description)
 * `language-new` : A new language has been added to the video. Either through the web UI (uploads or dialog) or through automatic transcription services.
 * `language-edit` : An existing language has been edited (title, description). Either through the web UI (uploads or dialog) or through automatic transcription services
 * `subs-new` : A new subtitle version has been created. Either through the web UI (uploads or dialog) or through automatic transcription services
 * `subs-approved` : Subtitles under moderation have been approved.
 * `subs-rejected` : Subtitles under moderation have been rejected.

* `team`: The slug for that team. The slug is a unique identifier that can be seen at the team's public url page.
* `project`:  The slug for that project. The slug is a unique identifier that can be seen at the project's video listing page.
* `video_id`: The video id used in Amara to identify that video.
* `api_url`: The URL for the Amara API that will have the latest data for that event (subtitles, language or videos)
* `language_code` : The human readable language code (i.e 'en' or 'es') for the this event. If the event is a language or subtitle event the language will be sent, else if it's a video event the parameter will be omitted. 

