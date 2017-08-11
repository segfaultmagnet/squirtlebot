# Name:         article.py
# Authors:      Matthew Sheridan
# time:         09 August 2017
# Revision:     09 August 2017
# Copyright:    Matthew Sheridan 2017
# Licence:      Beer-Ware License Rev. 42


__author__  = 'Matthew Sheridan'
__credits__ = ['Matthew Sheridan']
__time__    = '09 August 2017'
__version__ = '0.1'
__status__  = 'Development'


import time

from textblob import TextBlob

class Article:
  def __init__(self, url, title=None, blob=None):
    """
    Args:
      url:    the URL from which the article was retrieved or can be found

      title:  the title of the article

      blob:   the TextBlob representation of the article's content
    """
    self._set_url(url)
    self.set_title(title)
    self.set_blob(blob)

    self._time = None
    self._tags = self._build_tags()


# Accessors
  def blob(self):
    """ Returns the TextBlob representation of the article's content """
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


  def title(self):
    """ Returns the title of the article """
    return self._title


  def url(self):
    """ Returns the URL from which the article was retrieved or can be found """
    return self._url


# Mutators
  def set_blob(self, blob):
    """
    Sets self._blob and records the time at which the article was accesssed

    Args:
      blob:   the TextBlob representation of the article's content

    Raises:
      TypeError: if blob is not a TextBlob
    """
    assert type(blob) is TextBlob or blob == None, "arg 'blob' is not of type 'TextBlob': %r" % repr(type(blob))
    self._blob = blob
    self._time = time.gmtime()


  def set_title(self, title):
    """ Sets the title of the article """
    assert type(title) is str or title == None, "arg 'title' is not of type 'str': %r" % repr(type(title))
    self._title = title


  def _set_url(self, url):
    """ Sets the URL of the article """
    assert type(url) is str, "arg 'url' is not of type 'str': %r" % repr(type(url))
    self._url = url


# Private methods
  def _build_tags(self):
    """
    Returns a list of tags (team, player names) found in this article.
    """
    tags = []

    return tags
