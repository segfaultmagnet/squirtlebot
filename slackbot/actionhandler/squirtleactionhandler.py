__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

from random import randrange

from .actionhandler import *

class SquirtleActionHandler(ActionHandler):
  def __init__(self, name, at, cheeky=True, **kwargs):
    super(SquirtleActionHandler, self).__init__(name=name, at=at, **kwargs)
    self._inflect = inflect.engine()
    self.update(actions=self.actions_fantasy(), keywords=self.keywords_fantasy())
    if cheeky:
      self.update(actions=self.actions_cheeky(), keywords=self.keywords_cheeky())

  def exec_action(self, func, **kwargs):
    results = super(SquirtleActionHandler, self).exec_action(**kwargs)
    for r in results:
      func(kwargs['channel']['id'], r)
    return results

  def actions_cheeky(self):
    return [
      Action(name='brady', func=self._action_brady),
      Action(name='geno', func=self._action_geno),
      Action(name='jets', func=self._action_jets),
      Action(name='lacy', func=self._action_lacy),
    ]

  def actions_fantasy(self):
    return [
      Action(name='matchup', func=self._action_matchup),
      Action(name='tell', func=self._action_tell),
      # 'at_bot':  self._action_mention
    ]

  def keywords_cheeky(self):
    return [
      Keyword(name='brady', regex=re.compile('brady', flags=re.I)),
      Keyword(name='geno', regex=re.compile('[g]+[e]+[n]+[o]+', flags=re.I)),
      Keyword(name='jets', regex=re.compile('[j]+[-]*[e]+[-]*[t]+[-]*[s]+', flags=re.I)),
      Keyword(name='jets', regex=re.compile('fumble', flags=re.I)),
      Keyword(name='lacy', regex=re.compile('lacy', flags=re.I)),
      # Keyword(name='opinion', regex=re.compile(str(at + ' (what do you think|what\'s your opinion|what is your opinion) (of|about)'), flags=re.I), re_match=True),
    ]

  def keywords_fantasy(self):
    return [
      Keyword(name='tell', regex=re.compile('%s (?:tell me|what|how) about ([a-zA-Z]+)(?:\'|\'s) team' % self.at, flags=re.I), re_match=True),
      Keyword(name='matchup', regex=re.compile('%s show ([a-zA-Z]+)(?:\'|\'s)* matchup' % self.at), re_match=True),
      # 'at_bot':  [(re.compile(at, flags=re.I), True)]
    ]

  def _action_brady(self, **kwargs):
    return('Tom Brady has deflated balls.')

  def _action_geno(self, **kwargs):
    geno = []
    [geno.append('g') for _ in range(randrange(1,2))]
    [geno.append('e') for _ in range(randrange(2,4))]
    [geno.append('n') for _ in range(randrange(1,3))]
    [geno.append('o') for _ in range(randrange(2,5))]
    return(''.join(geno).upper())

  def _action_jets(self, **kwargs):
    return('GO JETS')

  def _action_lacy(self, **kwargs):
    return('Choo choo!')

  def _action_matchup(self, **kwargs):
    msg = []
    queried_player = re.findall(kwargs.get('regex'), kwargs.get('text'))[0]
    teams = kwargs.get('teams')
    week = kwargs.get('week')

    if queried_player.lower() == 'my':
      queried_player = kwargs['user']['first_name']
    player = None
    for p in kwargs.get('players'):
      if p.first_name.lower() == queried_player.lower():
        player = p

    team = None
    for t in teams:
      if t.owner_id == player.player_id:
        team = t
    opponent = team.schedule[week-1]

    msg.append('Week %s: vs. %s (%s)\n' % (week, opponent.owner, opponent.team_name))
    msg.append('%s: %s\n%s: %s' % (team.team_name, team.scores[week-1], opponent.team_name, opponent.scores[week-1]))
    return ''.join(msg)

  """ Needs to be updated.
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
  """

  # This is the next big one:
  # Add parsing for 'my' or move it up to SlackBot
  def _action_tell(self, **kwargs):
    msg = []
    team_owner = re.findall(kwargs.get('regex'), kwargs.get('text'))[0]
    teams      = kwargs.get('teams')
    teams_prev = kwargs.get('teams_prev')
    team_name       = None
    team_place_prev = None

    for t in teams:
      if t.owner.split()[0].lower() == team_owner.lower():
        team_name = t.team_name
    for t in teams_prev:
      if t.owner.split()[0].lower() == team_owner.lower():
        team_place_prev = t.overall_standing

    if team_name:
      msg.append(team_name + ' are terrible and %s is totally clueless.' % str.capitalize(team_owner))
      if team_place_prev:
        msg.append(' He somehow came in %s last year, but he\'ll manage to do worse this year.' % self._inflect.ordinal(team_place_prev))
    else:
      msg.append('I don\'t know who %s is, but I bet he sucks at fantasy.' % str.capitalize(team_owner))

    return ''.join(msg)
