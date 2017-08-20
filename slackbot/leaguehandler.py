"""
Primarily provides a wrapper for espnff's League class, but also provides some
functionality not supplied by espnff.
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

import json
import requests

from datetime import datetime, timedelta

from espnff import League

class LeagueHandler(object):
  def __init__(self, lid, year, espn_s2, swid, refresh_time=None):
    """
    Args:
      The same arguments required to insantiate espnff.League. If your version
      of the espnff package does not use the espn_s2 and swid arguments, check
      for a newer version at the maintainer's repo:
        https://github.com/rbarton65/espnff
      or use the forked version found at:
        https://github.com/segfaultmagnet/espnff

      lid:      League ID number
      year:     Year to fetch (season).
      espn_s2:  Cookie required for authentication. Retrieve this from your 
                browser cookies after logging in to ESPN.
      SWID:     Another cookie required for authentication.
    """
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
    """
    Returns a League object for the given year. If no year is given, the current
    year's League will be returned.
    """
    league = None
    if year in self._leagues and self._fetched[year] \
      and datetime.now() < (self._fetched[year] + timedelta(minutes=self._refresh_time)):
      league = self._leagues[year]
    else:
      league = self._fetch_league(year)
      self._current_week = self.current_week()
    return league

  def current_week(self):
    """ Returns the current week's number. """
    if not self._current_week:
      params = {
        'leagueId': self._lid,
        'seasonId': self._year
      }
      r = requests.get('http://games.espn.com/ffl/api/v2/scoreboard', params=params)
      data = r.json()
      self._current_week = data['scoreboard']['matchupPeriodId']
    return self._current_week

  def _fetch_league(self, year=None):
    """
    Called by self.get() if the League for the given year has not already been
    retrieved.
    """
    if not year:
      year = self._year
    try:
      league = League(self._lid, year, self._espn_s2, self._swid)
      self._fetched[year] = datetime.now()
    except:
      raise Exception('Error fetching league (year=' + repr(year) + ')')
    return league
