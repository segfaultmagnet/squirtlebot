__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

import os
import sys
import json
import re
import string
import threading
import time

from datetime import datetime, timedelta
from types import *

from espnff import League, Team
from slackclient import SlackClient
from textblob import TextBlob

from .actionhandler import SquirtleActionHandler
from .leaguehandler import LeagueHandler
from .slackbotlang import SlackBotLang
from .slackbotlib import SlackBotLib

class SlackBot(SlackBotLib, threading.Thread):
  def __init__(self, name, config, debug=False):
    super(SlackBot, self).__init__()

    self._config          = config
    self.DEBUG            = debug

    self.dbg = self._config['Logger'].debug
    self.info = self._config['Logger'].info
    self.warn = self._config['Logger'].warn
    self.err = self._config['Logger'].error
    self.crit = self._config['Logger'].critical

    self._client          = SlackClient(config['API_token'])
    self._classifier_path = os.path.relpath(config['Dat_dir'] + '/' + self.name_lower() + '.classifier', start=config['Root'])

    self._refreshtime     = 30
    self._run             = True
    self._sleeptime       = 1
    self._stopped         = False

    self._at              = None
    self._id              = None

    self.set_name(name)
    self._set_id(self.get_user_id(self.name_lower()))
    # self.init_classifier()
    self.init_channels()

  def run(self):
    if self.DEBUG:
      self.info('Starting in DEBUG mode.')
    else:
      self.info('Starting.')

    # Set up a new handlers and fetch the current year's league.
    actions = SquirtleActionHandler(self.name(), self.at())
    leagues = LeagueHandler(lid=self._config['League ID'],
                            year=self._config['League year'],
                            espn_s2=self._config['League_auth_cookies']['espn_s2'],
                            swid=self._config['League_auth_cookies']['SWID'])
    settings = leagues.get().settings
    if settings:
      self.info('League: ' + repr(settings.name) + ' (' + str(settings.year) + ')')
    else:
      raise Exception('League error.')

    # Connect.
    if self._client.rtm_connect():
      self.info('Connected as ' + repr(self.name()))

      # Respond to stuff where appropriate.
      while self._run == True:
        output = self.parse_rtm(self._client.rtm_read())

        if output['blob'] and output['channel']['name'] in self.channels().keys():
          action, text = actions.parse_keywords(text=str(output['blob']))
          result = None

          if action:
            args = {
              'action': action,
              'text': text
            }

            if action == 'tell':
              args['teams'] = leagues.get().teams
              args['teams_prev'] = leagues.get(2016).teams
              # args['team_owner'] = 

            result = actions.exec_action(**args)

          if result:
            self.post_msg(output['channel']['id'], result)

        time.sleep(1)

    self.info('Exiting.')
    self._stopped = True
    sys.exit()

  def parse_rtm(self, output):
    """
    Returns: if this bot is mentioned, a dict containing:
               a TextBlob of the message
               the channel in which it was sent
               the user who sent it
    """
    result = {'blob': None,
              'channel': {'name': None, 'id': None},
              'user': {'name': None, 'id': None}}
    if output and len(output) > 0:
      for o in output:
        if o and 'text' in o and o['user'] != self.id():
          result['blob']            = TextBlob(o['text'])
          result['channel']['id']   = o['channel']
          result['user']['id']      = o['user']
          result['channel']['name'] = self.get_channel_name(result['channel']['id'])
          result['user']['name']    = self.get_user_name(result['user']['id'])
        return result
    return result

  def channels(self):
    return self._config['Channels']

  def at(self):
    return str(self._at)

  def id(self):
    return str(self._id)

  def name(self):
    return str(self._name)

  def name_lower(self):
    return str(self._name.lower())

  def stopped(self):
    return self._stopped

  def _set_at(self, id_str):
    assert type(id_str) is str, 'ID is not a string.'
    self._at = '<@' + self.id() + '>'

  def _set_id(self, id_str):
    assert type(id_str) is str, 'ID is not a string.'
    self._id = id_str
    self._set_at(self.id())

  def set_name(self, name):
    assert type(name) is str, 'Name is not a string.'
    self._name = name

  def stop(self):
    self._run = False
