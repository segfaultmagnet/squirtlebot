__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

import time

class SlackBotLib:
  def at_user(self, id_str):
    return '<@' + id_str + '>.'

  def capitalize(self, string):
    string = string.strip(' \t').rstrip(' \t')
    if not string[0:2] == "<@":
      string = string[0:1].upper() + string[1:]
    return string

  def init_channels(self):
    """
    Fetches ID of each channel bot is allowed to use.
    """
    api_call = self._client.api_call('channels.list')
    if api_call.get('ok'):
      for c in api_call['channels']:
        if c['name'].lower() in self._config['Channels']:
          self._config['Channels'][c['name']] = c['id']

    api_call = self._client.api_call('groups.list')
    if api_call.get('ok'):
      for c in api_call['groups']:
        if c['name'].lower() in self._config['Channels']:
          self._config['Channels'][c['name']] = c['id']

  def get_channel_id(self, name):
    """
    Returns the ID associated with the given channel name.
    This includes both public and private channels.
    """
    id_str = None

    if name in self._config['Channels'].keys() and self._config['Channels'][name] != None:
      id_str = self._config['Channels'][name]

    else:
      api_call = self._client.api_call('channels.list')
      if api_call.get('ok'):
        channels = api_call.get('channels')
        for c in channels:
          if c['name'].lower() == name.lower():
            id_str = c['id']
            break
      else:
        raise Exception(api_call.get('error'))

      api_call = self._client.api_call('groups.list')
      if api_call.get('ok'):
        channels = api_call.get('groups')
        for c in channels:
          if c['name'].lower() == name.lower():
            id_str = c['id']
            break
      else:
        raise Exception(api_call.get('error'))

    return id_str

  def get_channel_name(self, id_str):
    """
    Returns the name associated with the given channel ID.
    This includes both public and private channels.
    """
    name = None

    if id_str in self._config['Channels'].values():
      name = (list(self._config['Channels'].keys())[list(self._config['Channels'].values()).index(id_str)])

    else:
      api_call = self._client.api_call('channels.list')
      if api_call.get('ok'):
        channels = api_call.get('channels')
        for c in channels:
          if c['id'].lower() == id_str.lower():
            name = c['name']
            break
      else:
        raise Exception(api_call.get('error'))

      api_call = self._client.api_call('groups.list')
      if api_call.get('ok'):
        channels = api_call.get('groups')
        for c in channels:
          if c['id'].lower() == id_str.lower():
            name = c['name']
            break
      else:
        raise Exception(api_call.get('error'))

    return name

  def get_user_id(self, name):
    """ Returns the ID associated with the given uesr name. """
    id_str = None

    api_call = self._client.api_call('users.list')
    if api_call.get('ok'):
      users = api_call.get('members')
      for u in users:
        if u['name'].lower() == name.lower():
          id_str = u['id']
          break
    else:
      raise Exception(api_call.get('error'))

    return id_str

  def get_user_name(self, id_str):
    """ Returns the name associated with the given uesr ID. """
    name = None

    api_call = self._client.api_call('users.list')
    if api_call.get('ok'):
      users = api_call.get('members')
      for u in users:
        if u['id'].lower() == id_str.lower():
          name = u['name']
          break
    else:
      raise Exception(api_call.get('error'))

    return name

  def post_msg(self, channel, msg):
    """ Sends a message to the given channel or user. """
    msg = self.capitalize(msg)
    self._client.api_call(
      'chat.postMessage',
      channel=channel,
      text=msg,
      as_user=True)
    self.dbg('Posted in ' + repr(self.get_channel_name(channel)) + ':\n ' + repr(msg))

"""
  def timestamp():
    ""
    Returns string of the local time formatted for logging.
    ""
    curr = time.localtime()
    stamp = '[' + Logger.int_to_str(curr.tm_mday, 2)   \
            + Logger.DAYS[curr.tm_wday]                \
            + str(curr.tm_year)[2:]                    \
            + ' ' + Logger.int_to_str(curr.tm_hour, 2) \
            + ':' + Logger.int_to_str(curr.tm_min, 2)  \
            + '] '

    return stamp
"""