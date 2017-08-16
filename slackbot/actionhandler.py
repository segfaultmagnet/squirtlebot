__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

import re

import inflect

# Define action and keyword structs?

class ActionHandler(object):
  def __init__(self, name):
    self.name = name
    self._actions  = {
      'about:author': self._action_about_author,
      'about:bot':    self._action_about_bot
    }
    """
    Keyword dictionaries should be formatted as follows:

    key (str): the action which should be taken
    value (tuple): a regex and a boolean (True to match at beginning of text,
      False to match anywhere in the text)
    """
    self._keywords = {
      'about:author': [(re.compile('segfaultmagnet', flags=re.I), False),
        (re.compile(__author__, flags=re.I), False)],
      'about:bot':    [(re.compile('about:' + name, flags=re.I), True)]
    }

  def exec_action(self, **kwargs):
    action = kwargs.get('action')
    if action and action in self._actions:
      return self._actions[action](**kwargs)
    return None

  def parse_keywords(self, **kwargs):
    text     = kwargs.get('text')
    action   = None
    text_new = None
    if text:
      for k in self._keywords:
        for c in self._keywords[k]:
          if (c[1] == True and c[0].match(text))     \
            or (c[1] == False and c[0].search(text)):
              action = k
              text_new = re.sub(c[0], '', text, count=1)
              break
    return action, text_new

  def _update(self, actions=None, keywords=None):
    if actions:
      new = {}
      new.update(self._actions)
      new.update(actions)
      self._actions = new

    if keywords:
      new = {}
      new.update(self._keywords)
      new.update(keywords)
      self._keywords = new

  def _action_about_author(self, **kwargs):
    return(__author__ + ' is the author of this bot. Please visit ' + repr(__website__) + '!')

  def _action_about_bot(self, **kwargs):
    return('slackbot is a chatbot created by ' + __author__)


class SquirtleActionHandler(ActionHandler):
  def __init__(self, name, at, **kwargs):
    super(SquirtleActionHandler, self).__init__(name, **kwargs)
    self.at = at
    self._inflect = inflect.engine()
    actions = {
      'brady':   self._action_brady,
      'geno':    self._action_geno,
      'jets':    self._action_jets,
      'tell':    self._action_tell,
      # 'at_bot':  self._action_mention
    }
    keywords = {
      'opinion': [(re.compile(str(at + ' (what do you think|what\'s your opinion|what is your opinion) (of|about)'), flags=re.I), True)],
      'say':     [(re.compile(str(at + ' say( that)*'), flags=re.I), True)],
      'tell':    [(re.compile(str(at + ' (tell me|what|how) about'), flags=re.I), True)],
      'brady':   [(re.compile('brady', flags=re.I), False)],
      'geno':    [(re.compile('[g]+[e]+[n]+[o]+', flags=re.I), False)],
      'jets':    [(re.compile('[j]+[-]*[e]+[-]*[t]+[-]*[s]+', flags=re.I), False),
                  (re.compile('fumble', flags=re.I), False)],
      # 'at_bot':  [(re.compile(at, flags=re.I), True)]
    }
    self._update(actions=actions, keywords=keywords)

  def _action_brady(self, **kwargs):
    return('Tom Brady has deflated balls.')

  def _action_geno(self, **kwargs):
    return('GEEENNNOOO')

  def _action_jets(self, **kwargs):
    return('GO JETS')

  def _action_mention(self, **kwargs):
    text = kwargs.get('text')
    user = kwargs.get('user')
    msg = None
    if text and user:
      if re.search('good night', text, flags=re.I):
        msg = 'Shoo, ' + self.at_user(user['id'])
      else:
        msg = 'Sup, ' + self.at_user(user['id'])
    return msg

  # This is the next big one:
  def _action_tell(self, **kwargs):
    teams      = kwargs.get('teams')
    teams_prev = kwargs.get('teams_prev')
    team_owner = re.sub('(\'s|\')', '', kwargs.get('text').split()[0], flags=re.I)
    team_name       = None
    team_place_prev = None

    for t in teams:
      if t.owner.split()[0].lower() == team_owner.lower():
        team_name = t.team_name
    for t in teams_prev:
      if t.owner.split()[0].lower() == team_owner.lower():
        team_place_prev = t.overall_standing

    if team_name:
      msg = team_name + ' are terrible and %s is totally clueless.' % str.capitalize(team_owner)
      if team_place_prev:
        msg += ' He somehow came in %s last year, but he\'ll manage to do worse this year.' % self._inflect.ordinal(team_place_prev)
    else:
      msg = 'I don\'t know who %s is, but I bet he sucks at fantasy.' % str.capitalize(team_owner)

    return msg
