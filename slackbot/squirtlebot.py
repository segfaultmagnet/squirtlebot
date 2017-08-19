__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet/squirtlebot'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

from .slackbot import *

from espnff import League, Team

from .actionhandler import SquirtleActionHandler
from .leaguehandler import LeagueHandler

class SquirtleBot(SlackBot):
  def __init__(self, name, config, debug=False):
    super(SquirtleBot, self).__init__(name=name, config=config, debug=debug)
    self._refreshtime = 30
    self._init_channels()

    if self.DEBUG:
      self.info('Starting in DEBUG mode.')
    else:
      self.info('Starting.')

  def run(self):
    self.league = LeagueHandler(lid=self._config['League ID'],
                                year=self._config['League year'],
                                espn_s2=self._config['League_auth_cookies']['espn_s2'],
                                swid=self._config['League_auth_cookies']['SWID'])
    settings = self.league.get().settings
    if settings:
      league_msg = '%s: League: %r (%s)' % (self.name(), settings.name, settings.year)
      self.info(league_msg)
      print(league_msg)

    super(SquirtleBot, self).run()

  def handle_actions(self, execute, **kwargs):
    results = []
    for e in execute:
      kwargs['action'] = e
      kwargs['regex'] = execute[e]

      if e == 'matchup':
        kwargs['teams'] = self.league.get().teams
        kwargs['players'] = self.league.get().players
        kwargs['week'] = self.league.current_week()

      if e == 'tell':
        kwargs['teams'] = self.league.get().teams
        kwargs['teams_prev'] = self.league.get(self._config['League year']-1).teams

      self.actions.exec_action(self.post_msg, **kwargs)

  def set_actions(self):
    self.actions = SquirtleActionHandler(self.name(), self.at(), cheeky=True)
