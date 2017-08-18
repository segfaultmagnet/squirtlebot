#!/usr/bin/env python3
"""
Utility for scraping webpages for football commentary. Currently configured to
scrape Deadspin for articles tagged with 'NFL'. Writes out a dict of Articles
keyed by their url

Usage:
  scraper.py <name> [--pages=<n>]
  scraper.py -h | --help
  scraper.py -v | --version

Arguments:
  <name>         The name of the slackbot which these articles are for.

Options:
  --pages=<n>    The number of index pages to look through for new articles
                 [default: 2].
  -h --help      Show this help message.
  -v, --version  Display program version number.
"""

__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet/squirtlebot'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

import os
import sys
import requests
import threading
import time

import _pickle as pickle

from collections import deque

from docopt import docopt
from lxml import html
from textblob import TextBlob

from .article import Article
from .articlescraper import ArticleScraper

class Scraper(threading.Thread):
  def __init__(self, articles_path, look_back_pages=2, page_increment=20):
    super(Scraper, self).__init__()

    self._articles_path = articles_path
    self._articles = self._load_articles(self._articles_path)

    self._look_back_pages = look_back_pages
    self._page_increment  = page_increment

    self._cached_index_page = None
    self._cached_index_url  = None
    self._run       = True
    self._stopped   = False

  def articles(self):
    return self._articles

  def stopped(self):
    return self._stopped

  def run(self):
    article_scraper = ArticleScraper()
    article_scraper.start()
    urls = []

    # Look at index pages and find those articles which have not been scraped
    page = 0
    perpage = 0
    while page < self._look_back_pages:
      urls    += self._get_article_urls('https://deadspin.com/tag/nfl?startIndex=' + str(perpage))
      page    += 1
      perpage += self._page_increment

    for u in urls:
      if not u in self._articles:
        article_scraper.append(str(u))

    # Collect scraped articles and write to file
    while self._run and len(article_scraper) > 0:
      new_article = article_scraper.pop_left()
      if new_article:
        self._articles[new_article.url()] = new_article
        # print('Got:  ' + repr(self._articles[new_article.url()].title()))
      
      time.sleep(1)

      self._dump_articles(self._articles, self._articles_path)

    # Clean up and stop
    print('Have ' + str(len(self._articles)) + ' articles.')
    article_scraper.stop()
    while not article_scraper.stopped():
      print('Waiting for ArticleScraper...')
      time.sleep(1)

    self._stopped = True

  def stop(self):
    self._run = False

  def _dump_articles(self, articles, path):
    """
    Writes the collected articles to file.

    Args:
      articles:   the list of articles to write to file

      path:       the path to write the articles to
    """
    with open(path, 'wb+') as out_file:
      pickle.dump(articles, out_file)

  def _load_articles(self, path):
    """
    Loads previously-saved articles from file.

    Args:
      path:   the path to load the articles from

    Returns:  a list of articles
    """
    articles = None
    try:
      with open(path, 'rb') as in_file:
        articles = pickle.load(in_file)
    except (EOFError, FileNotFoundError):
      return {}
    
    for a in articles:
      print('Read: ' + repr(articles[a].title()))

    return articles

  def _get_article_urls(self, url):
    """
    Args:
      url:    the URL of an index page which contains links to articles;
              e.g. https://deadspin.com/tag/nfl?startIndex=20

    Returns:  list of articles URLs to potentially scrape
    """

    index_page = self._cached_index_page
    if self._cached_index_url != url:
      self._cached_index_url  = url
      index_page = requests.get(url)
      self._cached_index_page = index_page

    tree = html.fromstring(index_page.content)
    urls = tree.xpath('//figure[@class="asset marquee-asset js_marquee-assetfigure "]/a[@href]/attribute::href')
    
    return urls

def __init__(args):
  root    = os.path.abspath(os.path.dirname(__file__))
  path    = os.path.normpath(root + '/../dat/' + args['<name>'] + '.articles')
  scraper = Scraper(path, look_back_pages=int(args['--pages']))
  scraper.start()

  try:
    cont = True
    while cont:
      time.sleep(1)
      cont = False

      if not scraper.stopped():
        cont = True

  except KeyboardInterrupt as k:
    print('Stopping.')
  finally:
    scraper.stop()
    print('Done.')

if __name__ == '__main__':
  __init__(docopt(__doc__, help=True, version=__version__))
  sys.exit()
