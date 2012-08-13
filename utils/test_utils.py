import urlparse


REQUEST_CALLBACKS = []

class Response(dict):

    status = 200
    content = ""

    def __getitem__(self, key):
        return getattr(self, key)

def reset_requests():
    global REQUEST_CALLBACKS
    REQUEST_CALLBACKS = []

def store_request_call(url, **kwargs):
    method = kwargs.pop('method', None)
    data = urlparse.parse_qs(kwargs.pop("body", ""))
    for k,v in data.items():
        data[k] = v[0]
    global REQUEST_CALLBACKS
    if not '/solr' in url:
        REQUEST_CALLBACKS.append([url, method, data])
    return Response(), ""

class TestCaseMessagesMixin(object):
    def _getMessagesCount(self, response, level=None):
        messages =  response.context['messages']
        if level:
            actual_num = len([x for x in messages if x.level==level])
        else:
            actual_num = len(messages)

        return actual_num

    def assertMessageCount(self, response, expect_num, level=None):
        """
        Asserts that exactly the given number of messages have been sent.
        """
        actual_num = self._getMessagesCount(response, level=level)
        if actual_num != expect_num:
            self.fail('Message count was %d, expected %d' %
                    (actual_num, expect_num)
                )

    def assertMessageEqual(self, response, text):
        """
        Asserts that the response includes the message text.
        """

        messages = [m.message for m in response.context['messages']]

        if text not in messages:
            self.fail(
                'No message with text "%s", messages were: %s' % 
                    (text, messages)
                )

    def assertMessageNotEqual(self, response, text):
        """
        Asserts that the response does not include the message text.
        """

        messages = [m.message for m in response.context['messages']]

        if text in messages:
            self.fail(
                'Message with text "%s" found, messages were: %s' % 
                    (text, messages)
                )
