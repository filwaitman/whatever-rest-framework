from __future__ import absolute_import, division, print_function, unicode_literals

import sys

if sys.version_info.major == 2:
    from urlparse import urlparse, parse_qsl, urlunparse
    from urllib import urlencode
    JSONDecodeError = ValueError

else:
    from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
    from json import JSONDecodeError
