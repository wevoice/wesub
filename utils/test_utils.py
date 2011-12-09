import mock
import urlparse

REQUEST_CALLBACKS = []

class Response(object):
    status = 200
    content = ""
    
def reset_requests():
    global REQUEST_CALLBACKS
    REQUEST_CALLBACKS = [] 

def store_request_call(url, **kwargs):
    method = kwargs.pop('method', None)
    data = urlparse.parse_qs(kwargs.pop("body", ""))
    for k,v in data.items():
        data[k] = v[0]
    global REQUEST_CALLBACKS
    REQUEST_CALLBACKS.append([url, method, data])
    return Response(), ""
