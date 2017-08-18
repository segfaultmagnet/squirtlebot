__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet/squirtlebot'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

import json
import requests

from datetime import datetime, timedelta

from espnff import League

class LeagueHandler(object):
  def __init__(self, lid, year, espn_s2, swid, refresh_time=None):
    self._lid      = lid
    self._year     = year
    self._espn_s2  = espn_s2
    self._swid     = swid
    self._current_week = None
    self._refresh_time = 30
    if refresh_time:
      self._refresh_time = refresh_time

    self._leagues  = {}
    self._fetched  = {}

  def get(self, year=None):
    league = None
    if year in self._leagues and self._fetched[year] \
      and datetime.now() < (self._fetched[year] + timedelta(minutes=self._refresh_time)):
      league = self._leagues[year]
    else:
      league = self._fetch_league(year)
      self._current_week = self._fetch_week()
    return league

  def current_week(self):
    if not self._current_week:
      self._fetch_week()
    return self._current_week

  def _fetch_league(self, year=None):
    if not year:
      year = self._year
    try:
      league = League(self._lid, year, self._espn_s2, self._swid)
      self._fetched[year] = datetime.now()
    except:
      raise Exception('Error fetching league (year=' + repr(year) + ')')
    return league

  def _fetch_week(self):
    params = {
      'leagueId': self._lid,
      'seasonId': self._year
    }
    r = requests.get('http://games.espn.com/ffl/api/v2/scoreboard', params=params)
    data = r.json()
    return data['scoreboard']['matchupPeriodId']
