import requests

def url_exists(url):
    """Check that a url (when following redirection) exists.

    This is needed because Django's validators rely on Python's urllib2
    which in verions < 2.6 won't follow redirects.

    """
    try:
        return 200 <= requests.head(url).status_code < 400
    except requests.ConnectionError:
        return False
