========================
HTTP Callbacks for Teams
========================

Enterprise customers can register an http callback so that activity on their
teams will fire an HTTP POST request.

To register your Team to receive HTTP notfications get in contact with us,
this process is done manually, there is no UI for this over the website at the
moment.

Pick a URL where you'd like to get notified. Each team can have their own
URL, or a URL can be used amongst serveral teams (for example in a public /
private team setup) We recomend the URL uses https for safer communication.

Notification Details
====================

We can send notifications for various events, depending on what your team is interested in.  Some examples are:

 * A new video is added through the team
 * Video data is edited (video url, title, description)
 * A new subtitle version is added to one of your videos
 * Subtitles are published for one of your videos
 * A Team member is added/removed
 * A Team member's profile information changes

For each event we can customize the data that is sent with the notification.
This includes anything available via the API.

Also, each notification will include a number in the POST data.  This is an
integer that increments by 1 for each notification we send you.  You can use
the number field to check if you missed any notifications.

To view previously sent notifications use the :ref:`Team Notifications API <api_notifications>`.
