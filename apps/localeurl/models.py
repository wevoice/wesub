
# This needs to run as soon as possible, models.py gets imported before
# urls.py so this seems like a good time.

from localeurl import patch_reverse
patch_reverse()


