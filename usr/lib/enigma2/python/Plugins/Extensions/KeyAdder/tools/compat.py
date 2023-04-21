# Source code from (https://github.com/Taapat/enigma2-plugin-youtube/blob/master/src/compat.py)
from sys import version_info

PY3 = version_info[0] == 3


# Disable certificate verification on python 2.7.9
if version_info >= (2, 7, 9):
	import ssl
	ssl._create_default_https_context = ssl._create_unverified_context


if version_info[0] == 2:
	# Python 2
	compat_str = unicode

	from urllib import urlencode as compat_urlencode
	from urllib import quote as compat_quote
	from urllib2 import urlopen
	from urllib2 import Request as compat_Request
	from urllib2 import HTTPError as compat_HTTPError
	from urllib2 import URLError as compat_URLError
	from urlparse import urljoin as compat_urljoin
	from urlparse import urlparse as compat_urlparse
	from urlparse import parse_qs as compat_parse_qs
	from urlparse import urlunparse as compat_urlunparse
	from httplib import HTTPException as compat_HTTPException
else:
	# Python 3
	compat_str = str

	from urllib.parse import urlencode as compat_urlencode
	from urllib.parse import quote as compat_quote
	from urllib.request import urlopen
	from urllib.request import Request as compat_Request
	from urllib.error import HTTPError as compat_HTTPError
	from urllib.error import URLError as compat_URLError
	from urllib.parse import urljoin as compat_urljoin
	from urllib.parse import urlparse as compat_urlparse
	from urllib.parse import parse_qs as compat_parse_qs
	from urllib.parse import urlunparse as compat_urlunparse
	from http.client import HTTPException as compat_HTTPException

def compat_urlopen(url, timeout=5):
	"""
	Urlopen in thread to enforce a timeout on the function call.
	Timeout in urlopen only affects how long Python waits before
	an exception is raised if the server has not issued a response.
	It does not enforce a time limit on the entire function call.
	"""
	compat_urlopen.response = None
	compat_urlopen.error = None

	def open_url(url, timeout):
		try:
			compat_urlopen.response = urlopen(url, timeout=timeout)
		except Exception as e:
			compat_urlopen.error = e

	t = Thread(target=open_url, args=(url, timeout))
	t.setDaemon(True)
	t.start()
	t.join(timeout + 1)
	if compat_urlopen.error:
		raise compat_urlopen.error
	return compat_urlopen.response
