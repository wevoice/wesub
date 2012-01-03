import httplib2

def url_exists(url):
    """Check that a url- when following redirection - exists.

    This is needed because django's validators rely on python's urllib2
    which in verions < 2.6 won't follow redirects.

    """
    h = httplib2.Http()
    try:
        resp, content = h.request(url, method="HEAD")
    except httplib2.ServerNotFoundError:
        return False
    h.follow_all_redirects = True
    return 200 <= resp.status < 400
