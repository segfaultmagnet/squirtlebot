__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

class SlackBotLib:
  def at_user(id_str):
    return '<@' + id_str + '>.'

  def init_channels(client, channels):
    """
    Fetches ID of each channel bot is allowed to use.
    """
    result = channels
    api_call = client.api_call('channels.list')
    if api_call.get('ok'):
      for c in api_call['channels']:
        if c['name'].lower() in result:
          result[c['name']] = c['id']

    api_call = client.api_call('groups.list')
    if api_call.get('ok'):
      for c in api_call['groups']:
        if c['name'].lower() in result:
          result[c['name']] = c['id']

    return result

  def channel_id(client, channels, name):
    """
    Returns the ID associated with the given channel name.
    This includes both public and private channels.
    """
    id_str = None

    if name in channels.keys() and channels[name] != None:
      id_str = channels[name]

    else:
      api_call = client.api_call('channels.list')
      if api_call.get('ok'):
        channels = api_call.get('channels')
        for c in channels:
          if c['name'].lower() == name.lower():
            id_str = c['id']
            break
      else:
        raise Exception(api_call.get('error'))

      api_call = client.api_call('groups.list')
      if api_call.get('ok'):
        channels = api_call.get('groups')
        for c in channels:
          if c['name'].lower() == name.lower():
            id_str = c['id']
            break
      else:
        raise Exception(api_call.get('error'))

    return id_str

  def channel_name(client, channels, id_str):
    """
    Returns the name associated with the given channel ID.
    This includes both public and private channels.
    """
    name = None

    if id_str in channels.values():
      name = (list(channels.keys())[list(channels.values()).index(id_str)])

    else:
      api_call = client.api_call('channels.list')
      if api_call.get('ok'):
        channels = api_call.get('channels')
        for c in channels:
          if c['id'].lower() == id_str.lower():
            name = c['name']
            break
      else:
        raise Exception(api_call.get('error'))

      api_call = client.api_call('groups.list')
      if api_call.get('ok'):
        channels = api_call.get('groups')
        for c in channels:
          if c['id'].lower() == id_str.lower():
            name = c['name']
            break
      else:
        raise Exception(api_call.get('error'))

    return name

  def user_id(client, name):
    """ Returns the ID associated with the given uesr name. """
    id_str = None

    api_call = client.api_call('users.list')
    if api_call.get('ok'):
      users = api_call.get('members')
      for u in users:
        if u['name'].lower() == name.lower():
          id_str = u['id']
          break
    else:
      raise Exception(api_call.get('error'))

    return id_str

  def user_name(client, id_str):
    """ Returns the name associated with the given uesr ID. """
    name = {}

    api_call = client.api_call('users.list')
    if api_call.get('ok'):
      users = api_call.get('members')
      for u in users:
        if u['id'].lower() == id_str.lower():
          name['name'] = u['name']
          name['first_name'] = u['profile']['first_name']
          # name['last_name'] = u['profile']['last_name']
          break
    else:
      raise Exception(api_call.get('error'))

    return name
