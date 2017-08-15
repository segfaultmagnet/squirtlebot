# Name:         slackbot.py
# Authors:      Matthew Sheridan
# Date:         04 August 2017
# Revision:     10 August 2017
# Revision:     08 August 2017
# Copyright:    Matthew Sheridan 2017
# Licence:      Beer-Ware License Rev. 42


__author__  = 'Matthew Sheridan'
__credits__ = ['Matthew Sheridan']
__date__    = '08 August 2017'
__version__ = '0.1'
__status__  = 'Development'

import os
import sys
import json
import re
import string
import threading
import time

from types import *

import inflect

from espnff import League, Team
from slackclient import SlackClient

from .slackbotlang import SlackBotLang
from .slackbotlib import SlackBotLib


class SlackBot(SlackBotLang, SlackBotLib, threading.Thread):
  def __init__(self, name, config, debug=False):
    super(SlackBot, self).__init__()

    self.DEBUG            = debug
    self._logger          = config['Logger']

    self._client          = SlackClient(config['API_token'])
    self._channels        = config['Channels']
    self._classifier_path = os.path.relpath(config['Dat_dir'] + '/' + self.name_lower() + '.classifier', start=config['Root'])
    self._league          = League(config['League ID'],
                                   config['League year'], 
                                   espn_s2=config['League_auth_cookies']['espn_s2'],
                                   swid=config['League_auth_cookies']['SWID'])
    self._league_prev     = League(config['League ID'],
                                   config['League year'] - 1, 
                                   espn_s2=config['League_auth_cookies']['espn_s2'],
                                   swid=config['League_auth_cookies']['SWID'])

    self._run             = True
    self._sleeptime       = 1
    self._stopped         = False

    self._at              = None
    self._id              = None
    self._p               = inflect.engine()
    self.commands         = {}
    self.keywords         = {}

    self.set_name(name)
    self.set_id(self.get_user_id(self.name_lower()))
    self.set_commands()
    self.set_keywords()
    self.init_classifier()
    self.init_channels()


  def run(self):
    if self.DEBUG == True:
      self.log('Starting in DEBUG mode.')
    else:
      self.log('Starting.')

    if self._league:
      settings = self._league.settings
      self.log('League: ' + repr(settings.name) + ' (' + str(settings.year) + ')')

    # Connect.
    if self._client.rtm_connect():
      self.log('Connected.')

    # Respond to stuff.
    while self._run == True:
      output = self.parse_rtm(self._client.rtm_read())
      if output['blob']:
        self.log(repr(output['user']['name']) + ' in '
                 + repr(output['channel']['name']) + ':\n  \''
                 + str(output['blob']) + '\'')

        # Only output to channels allowed.
        if output['channel']['name'] in self._channels.keys():
          self.handle_action(output)

      time.sleep(1)

    self.log('Exiting.')
    self._stopped = True
    sys.exit()


  def handle_action(self, output):
    """
    Give an appropriate and clever response (maybe).
    """
    action  = output['action'].lower()
    blob    = output['blob']
    channel = output['channel']
    user    = output['user']

    if action == 'brady':
      self.post_msg(channel['id'], 'Eat my nards, Tom Brady.')

    elif action == 'geno':
      self.post_msg(channel['id'], 'GEEENNNOOO')

    elif action == 'buttfumble' or action == 'jets':
      self.post_msg(channel['id'], 'GO JETS')

    elif action == 'mention':
      if re.search('good night', str(blob), flags=re.I):
        self.post_msg(channel['id'], 'Shoo, ' + self.at_user(user['id']))
      else:
        self.post_msg(channel['id'], 'Sup, ' + self.at_user(user['id']))

    if action == 'at_bot':
      text = re.sub(self.at() + ' ', '', str(blob), count=1)
      command, text = self.parse_commands(text)
      words = text.strip(string.punctuation).split()
      msg = ''

      if command == 'opinion':
        msg = ' '.join(words)
        if msg[len(msg)-1].lower() == 's':
          msg += ' are'
        else:
          msg += ' is'
        self.post_msg(channel['id'], msg + ' really, truly terrible.')

      elif command == 'say':
        self.post_msg(channel['id'], text)

      elif command == 'tell':
        teams = self._league.teams
        teams_prev = self._league_prev.teams
        team_owner = re.sub('\'s', '', words[0], flags=re.I)
        team_name       = None
        team_place_prev = None

        for t in teams:
          if t.owner.split()[0].lower() == team_owner.lower():
            team_name = t.team_name
        for t in teams_prev:
          if t.owner.split()[0].lower() == team_owner.lower():
            team_place_prev = t.overall_standing

        if team_name:
          msg = team_name + ' are terrible and ' + self.capitalize(team_owner) \
                + ' is totally clueless.'
          if team_place_prev:
            msg += ' He somehow came in ' + self._p.ordinal(team_place_prev) \
                   + ' last year, but he\'ll manage to do worse this year.'
        else:
          msg = 'I don\'t know who ' + self.capitalize(team_owner) \
                + ' is, but I bet he sucks at fantasy.'

        self.post_msg(channel['id'], msg)

      else:
        self.post_msg(channel['id'], 'What do you want?')

    return
