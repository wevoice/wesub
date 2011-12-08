import mock
import urlparse

REQUEST_CALLBACKS = []

class Response(object):
    status = 200
    content = ""
    
def reset_requests():
    global REQUEST_CALLBACKS
    REQUEST_CALLBACKS = [] 

def add_call(url, **kwargs):
    method = kwargs.pop('method', None)
    data = kwargs.pop("data", {})
    global REQUEST_CALLBACKS
    REQUEST_CALLBACKS.append([url, method, data])
    return Response(), ""
