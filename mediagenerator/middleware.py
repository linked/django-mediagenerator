from .settings import DEV_MEDIA_URL, MEDIA_DEV_MODE
from django.utils.cache import patch_cache_control
from django.utils.http import http_date
import time

class MediaMiddleware(object):
    """
    Middleware for handling correct caching of media files. Removes
    ETags from media files to save unnecessary roundtrips.
    """

    MAX_AGE = 60*60*24*365

    def process_response(self, request, response):
        if not MEDIA_DEV_MODE or not request.path.startswith(DEV_MEDIA_URL):
            return response

        for header in ('ETag', 'Expires', 'Cache-Control', 'Vary'):
            if response.has_header(header):
                del response[header]

        # Cache manifest files MUST NEVER be cached or you'll be unable to update
        # your cached app!!!
        if response['Content-Type'] != 'text/cache-manifest' and \
                response.status_code == 200:
            patch_cache_control(response, public=True, max_age=self.MAX_AGE)
            response['Expires'] = http_date(time.time() + self.MAX_AGE)
        return response
