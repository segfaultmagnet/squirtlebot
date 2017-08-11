# Name:         articlescraper.py
# Authors:      Matthew Sheridan
# Date:         10 August 2017
# Revision:     10 August 2017
# Copyright:    Matthew Sheridan 2017
# Licence:      Beer-Ware License Rev. 42

"""
Scrapes list of articles. Currently configured to scrape Deadspin for articles
tagged with 'NFL'.
"""


import requests
import threading
import time

from collections import deque

from lxml import html
from textblob import TextBlob

from article import Article


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


# Accessors
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


# Mutators
  def append(self, url):
    assert type(url) is str, "arg 'url' is not of type 'str': %r" % repr(type(url))
    self._url_deque.append(str(url))


  def stop(self):
    self._run = False


# Private methods
  def _get_article(self, url):
    """
    Args:
      url:    the URL of the article

    Returns:
      the TextBlob representation of an article's content

      the title of the article
    """
    assert type(url) is str, "arg 'url' is not of type 'str': %r" % repr(type(url))
    content = ''
    title   = ''

    page = requests.get(url)
    tree = html.fromstring(page.content)
    paras = tree.xpath('//div[@class="post-content entry-content js_entry-content "]/p')
    for p in paras:
      content += str(p.text_content()) + '\n'
    header = tree.xpath('//h1[@class="headline hover-highlight entry-title js_entry-title"]/a')
    title = str(header[0].text_content())

    return TextBlob(content), title
