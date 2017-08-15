# Name:         slackbotlib.py
# Authors:      Matthew Sheridan
# Date:         05 August 2017
# Revision:     08 August 2017
# Copyright:    Matthew Sheridan 2017
# Licence:      Beer-Ware License Rev. 42


__author__  = 'Matthew Sheridan'
__credits__ = ['Matthew Sheridan']
__date__    = '08 August 2017'
__version__ = '0.1'
__status__  = 'Development'


class SlackBotLib:
# Accessors.
  def channels(self):
    return self._channels

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


# Mutators.
  def set_at(self, id_str):
    assert type(id_str) is str, 'ID is not a string.'
    self._at = '<@' + self.id() + '>'

  def set_id(self, id_str):
    assert type(id_str) is str, 'ID is not a string.'
    self._id = id_str
    self.set_at(self.id())

  def set_name(self, name):
    assert type(name) is str, 'Name is not a string.'
    self._name = name

  def stop(self):
    self._run = False


# Bot actions.
  def post_msg(self, channel, msg):
    """ Sends a message to the given channel or user. """
    msg = self.capitalize(msg)
    self._client.api_call(
      'chat.postMessage',
      channel=channel,
      text=msg,
      as_user=True)
    self.log('Posted in ' + repr(self.get_channel_name(channel)) + ':\n ' + repr(msg))


# Utilities.
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
        if c['name'].lower() in self._channels:
          self._channels[c['name']] = c['id']

    api_call = self._client.api_call('groups.list')
    if api_call.get('ok'):
      for c in api_call['groups']:
        if c['name'].lower() in self._channels:
          self._channels[c['name']] = c['id']


  def get_channel_id(self, name):
    """
    Returns the ID associated with the given channel name.
    This includes both public and private channels.
    """
    id_str = None

    if name in self._channels.keys() and self._channels[name] != None:
      id_str = self._channels[name]

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

    if id_str in self._channels.values():
      name = (list(self._channels.keys())[list(self._channels.values()).index(id_str)])

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


  def log(self, msg):
    string = self.name() + ': ' + str(msg)
    print(string)
    self._logger.add(string)
