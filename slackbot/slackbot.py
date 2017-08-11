# Name:         slackbot.py
# Authors:      Matthew Sheridan
# Date:         04 August 2017
<<<<<<< HEAD
# Revision:     10 August 2017
=======
# Revision:     08 August 2017
>>>>>>> 01c16d7ce50795e550a75700f26eac35c285789e
# Copyright:    Matthew Sheridan 2017
# Licence:      Beer-Ware License Rev. 42


__author__  = 'Matthew Sheridan'
__credits__ = ['Matthew Sheridan']
__date__    = '08 August 2017'
__version__ = '0.1'
__status__  = 'Development'

import os
import sys
import re
import threading
import time

from types import *

from slackclient import SlackClient

from .slackbotlang import SlackBotLang
from .slackbotlib import SlackBotLib


class SlackBot(threading.Thread, SlackBotLang, SlackBotLib):
  def __init__(self, name, config, debug=False):
    super(SlackBot, self).__init__()

    self.DEBUG            = debug
    self._logger          = config['Logger']

    self._client          = SlackClient(config['API_token'])
    self._channels        = config['Channels']
    self._classifier_path = os.path.relpath(config['Dat_dir'] + '/' + self.name_lower() + '.classifier', start=config['Root'])
    self._auth_cookies    = config['League_auth_cookies']

    self._run             = True
    self._sleeptime       = 1
    self._stopped         = False

    self._at              = None
    self._id              = None
    self.keywords         = {}
    self.set_name(name)
    self.set_id(self.get_user_id(self.name_lower()))
    self.set_keywords()
    self.init_classifier()
    self.init_channels()


  def run(self):
    if self.DEBUG == True:
      self.log('Starting in DEBUG mode.')
    else:
      self.log('Starting.')

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


  def set_keywords(self):
    """
    Keywords for which the bot should return pre-defined responses, including
    @bot mentions.
    """
    self.keywords = {
      'search': {
        'brady':      re.compile('brady', flags=re.I),
        'buttfumble': re.compile('fumble', flags=re.I),
        'geno':       re.compile('[g]+[e]+[n]+[o]+', flags=re.I),
        'jets':       re.compile('[j]+[-]*[e]+[-]*[t]+[-]*[s]+', flags=re.I),
        'mention':    re.compile(str(self.at())),
      },
      'match': {
        'at_bot':     re.compile(str(self.at()), flags=re.I)
      }}


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

    elif action == 'at_bot':
      newtext = re.sub(self.at() + ' ', '', str(blob), count=1)
      words   = newtext.split()

      msg = ''

      if words:
        says = ['say', 'say that']
        for s in says:
          if re.match(s, newtext, flags=re.I):
            msg = re.sub(s, '', newtext, count=1, flags=re.I)

        opinions = ['what do you think', 'what\'s your opinion',
                    'what is your opinion']
        for o in opinions:
          for p in ['of', 'about']:
            if re.match(str(o + ' ' + p), newtext, flags=re.I):
              msg = re.sub(str(o + ' ' + p), '', newtext, count=1, flags=re.I)
              msg = re.sub('[?!]', '', msg, flags=re.I)
              msg = msg + ' is really, truly terrible.'

      else:
        msg = 'What do you want?'

      self.post_msg(channel['id'],  msg)

    return
