__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet/squirtlebot'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

import time

from textblob import TextBlob

class Article(object):
  def __init__(self, url, title=None, blob=None):
    """
    Args:
      url:    the URL from which the article was retrieved or can be found

      title:  the title of the article

      blob:   the TextBlob representation of the article's content
    """
    self.url(url=url)
    self.title(title=title)
    self.blob(blob=blob)

    self._time = None
    self._tags = self._build_tags()

  def blob(self, blob=None):
    """
    Sets self._blob and records the time at which the article was accesssed

    Args:
      blob:  the TextBlob representation of the article's content

    Returns: the TextBlob representation of the article's content

    Raises:
      TypeError: if blob is not a TextBlob
    """
    if blob:
      assert type(blob) is TextBlob or blob == None, "arg 'blob' is not of type 'TextBlob': %r" % repr(type(blob))
      self._blob = blob
      self._time = time.gmtime()
    return self._blob

  def content(self):
    """ Returns the string representation of the article's content """
    return str(self._blob)

  def tags(self):
    """
    Returns tags associated with this article, particularly player and/or
    team names
    """
    return self._tags

  def time(self):
    """ Returns the GMT time at which this article was retrieved """
    return self._time

  def title(self, title=None):
    """ Returns the title of the article """
    if title:
      assert type(title) is str or title == None, "arg 'title' is not of type 'str': %r" % repr(type(title))
      self._title = title
    return self._title

  def url(self, url=None):
    """ Returns the URL from which the article was retrieved or can be found """
    if url:
      assert type(url) is str, "arg 'url' is not of type 'str': %r" % repr(type(url))
      self._url = url
    return self._url

  def _build_tags(self):
    """
    Returns a list of tags (team, player names) found in this article.
    """
    tags = []

    return tags
