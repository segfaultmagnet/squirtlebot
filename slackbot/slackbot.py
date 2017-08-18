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
import threading
import time

from datetime import datetime, timedelta
from types import *

from slackclient import SlackClient
from textblob import TextBlob

from .actionhandler import ActionHandler
from .slackbotlib import SlackBotLib

class SlackBot(threading.Thread):
  def __init__(self, name, config, debug=False):
    super(SlackBot, self).__init__()
    self._config = config
    self.DEBUG   = debug
    self._at   = None
    self._id   = None
    self._name = None

    self.dbg  = self._config['Logger'].debug
    self.info = self._config['Logger'].info
    self.warn = self._config['Logger'].warn
    self.err  = self._config['Logger'].error
    self.crit = self._config['Logger'].critical

    self._client = SlackClient(config['API_token'])

    self._run         = True
    self._sleeptime   = 1
    self._stopped     = False

    self.name(name)
    self.id(self._user_id(self.name_lower()))
    self._init_channels()

    if self.DEBUG:
      self.info('Starting in DEBUG mode.')
    else:
      self.info('Starting.')

    self.actions = ActionHandler(self.name(), self.at())

  def run(self):
    # Connect.
    if self._client.rtm_connect():
      connect_msg = 'Connected as ' + repr(self.name())
      self.info(connect_msg)
      print(connect_msg)

      # Respond to stuff where appropriate.
      while self._run == True:
        output = self.parse_rtm(self._client.rtm_read())
        if output['blob'] and output['channel']['name'] in self.channels().keys():
          execute = self.actions.parse_keywords(text=str(output['blob']))
          if execute:
            args = {
              'text': str(output['blob']),
              'channel': output['channel'],
              'user': output['user'],
            }
            self.handle_action(execute, **args)
        time.sleep(self._sleeptime)

    self.info('Exiting.')
    self._stopped = True
    sys.exit()

  def handle_action(self, execute, **kwargs):
    results = []
    for e in execute:
      self.actions.exec_action(self.post_msg, **kwargs)

  def parse_rtm(self, output):
    """
    Returns a dict containing:
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
          result['channel']['name'] = self._channel_name(result['channel']['id'])
          user = self._user_name(result['user']['id'])
          result['user']['name']       = user['name']
          result['user']['first_name'] = user['first_name']
          # result['user']['last_name']  = user['last_name']
        return result
    return result

  def post_msg(self, channel, msg):
    """ Sends a message to the given channel or user. """
    self._client.api_call(
      'chat.postMessage',
      channel=channel,
      text=msg,
      as_user=True)
    self.dbg('Posted in ' + repr(self._channel_name(channel)) + ':\n ' + repr(msg))

  def at(self, id_str=None):
    if id_str:
      assert type(id_str) is str, 'ID is not a string.'
      self._at = '<@' + id_str + '>'
    return str(self._at)

  def id(self, id_str=None):
    if id_str:
      assert type(id_str) is str, 'ID is not a string.'
      self._id = id_str
      self.at(self._id)
    return str(self._id)

  def channels(self):
    return self._config['Channels']

  def name(self, name=None):
    if name:
      assert type(name) is str, 'Name is not a string.'
      self._name = name
    return str(self._name)

  def name_lower(self):
    return str(self.name().lower())

  def stopped(self):
    return self._stopped

  def stop(self):
    self._run = False

  def _init_channels(self):
    self._config['Channels'] = SlackBotLib.init_channels(
      client=self._client,
      channels=self.channels())

  def _channel_id(self, name):
    return SlackBotLib.channel_id(
      client=self._client,
      channels=self.channels(),
      name=name)

  def _channel_name(self, id_str):
    return SlackBotLib.channel_name(
      client=self._client,
      channels=self.channels(),
      id_str=id_str)

  def _user_id(self, name):
    return SlackBotLib.user_id(self._client, name)

  def _user_name(self, id_str):
    return SlackBotLib.user_name(self._client, id_str)
