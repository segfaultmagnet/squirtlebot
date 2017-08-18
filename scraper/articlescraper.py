"""
Scrapes list of articles. Currently configured to scrape Deadspin for articles
tagged with 'NFL'.
"""

__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

import requests
import threading
import time

from collections import deque

from lxml import html
from textblob import TextBlob

from .article import Article

class ArticleScraper(threading.Thread):
  def __init__(self):
    super(ArticleScraper, self).__init__()

    self._article_deque = deque()
    self._url_deque     = deque()

    self._run = True
    self._stopped = False

  def run(self):
    while self._run:
      if self._url_deque:
        u = self._url_deque.popleft()
        blob, title = self._get_article(u)
        self._article_deque.append(Article(u, title=title, blob=blob))
      time.sleep(1)

    self._stopped = True

  def __len__(self):
    return len(self._url_deque)

  def pop_left(self):
    """
    Returns:  first article in the deque
    """
    new_article = None
    try:
      new_article = self._article_deque.popleft()
    except IndexError:
      pass
    return new_article

  def stopped(self):
    return self._stopped

  def append(self, url):
    assert type(url) is str, "arg 'url' is not of type 'str': %r" % repr(type(url))
    self._url_deque.append(str(url))

  def stop(self):
    self._run = False

  def _get_article(self, url):
    """
    Args:
      url:    the URL of the article

    Returns:
      the TextBlob representation of an article's content

      the title of the article
    """
    assert type(url) is str, "arg 'url' is not of type 'str': %r" % repr(type(url))
    content = []
    title   = ''

    page = requests.get(url)
    tree = html.fromstring(page.content)
    paras = tree.xpath('//div[@class="post-content entry-content js_entry-content "]/p')
    for p in paras:
      content.append(str(p.text_content()) + '\n')
    header = tree.xpath('//h1[@class="headline hover-highlight entry-title js_entry-title"]/a')
    title = str(header[0].text_content())

    return TextBlob(''.join(content)), title
