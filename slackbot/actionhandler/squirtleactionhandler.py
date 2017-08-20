"""
Defines the behavior of the SquirtleBot. Subclass of ActionHandler. This subclass
does not override the default Actions and Keywords of its parent class, but does
override exec_action method to allow another function to be called after the
execution of each Action's function.
"""

__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet/squirtlebot'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

from random import randrange

from .actionhandler import *

class SquirtleActionHandler(ActionHandler):
  def __init__(self, name, at, cheeky=True, **kwargs):
    """
    Args:
      Same as those required by parent class ActionHandler with the addition of
      a bool 'cheeky' which controls whether or not this bot should enable its
      less useful but more fun behaviors. Optional; not for Patriots fans.
    """
    super(SquirtleActionHandler, self).__init__(name=name, at=at)
    self._inflect = inflect.engine()
    self.update(actions=self.actions_fantasy(), keywords=self.keywords_fantasy())
    if cheeky:
      self.update(actions=self.actions_cheeky(), keywords=self.keywords_cheeky())

  def exec_action(self, function=None, **kwargs):
    results = super(SquirtleActionHandler, self).exec_action(**kwargs)
    for r in results:
      kwargs['result'] = r
      if function:
        function(**kwargs)
    return results

  """
  The following methods simply return lists which will be merged with
  self._actions and self._keywords. They are separated here as their own methods
  for ease of use and readability.
  """

  def actions_cheeky(self):
    return [
      Action(name='brady', function=self._action_brady),
      Action(name='geno', function=self._action_geno),
      Action(name='jets', function=self._action_jets),
      Action(name='lacy', function=self._action_lacy),
    ]

  def actions_fantasy(self):
    return [
      Action(name='matchup', function=self._action_matchup),
      Action(name='matchups_all', function=self._action_matchups_all),
      Action(name='tell', function=self._action_tell),
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
      Keyword(name='matchup', regex=re.compile('%s show (?!all)([a-zA-Z]+)(?:\'|\'s){0,1} matchup' % self.at), re_match=True),
      Keyword(name='matchups_all', regex=re.compile('%s show all matchups' % self.at), re_match=True),
      Keyword(name='tell', regex=re.compile('%s (?:tell me|what|how) about ([a-zA-Z]+)(?:\'|\'s){0,1} team' % self.at, flags=re.I), re_match=True),
      # 'at_bot':  [(re.compile(at, flags=re.I), True)]
    ]

  """
  The following are methods which should be executed when an Action is called
  (see the Action instances above in self._actions). If the SlackBot should post
  a message to the channel that prompted the Action, that message should be
  returned by these methods.
  """

  def _action_brady(self, **kwargs):
    return('Tom Brady has deflated balls.')

  def _action_geno(self, **kwargs):
    """
    Returns a string similar to 'GENO' with a random number of 'E', 'N', and
    'O' characters.
    """
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
    """
    Returns the matchup and scores for a given player during a given week.

    Args in kwargs:
      players:  A list of Player objects. This will be used to match a Slack user
                to a member of the fantasy league, and that member to their team.
                See: espnff.Player

      regex:  The regular expression which matched the Action containing this
              method. Necessary to retrieve the name of the person whose matchup
              should be returned.

      teams:  A list of Team objects, one for each team in the league.
              See: espnff.Team

      text:   The text content of the message in which the request was made.

      user:   The user whose message triggered this method. This is not necessarily
              the person whose matchup should be fetched. Their first name must
              be supplied as well, as this will be used to match a Slack user to
              a member of the fantasy league. If your league has people with the
              same first name, you may wish to change this behavior. This will
              likely be made more robust in the future.

      week:   The week number of the matchup to be fetched. Note: this does NOT
              start at zero. Range: in all likelihood, 1 to 16.
    """
    msg = []
    queried_player = re.findall(kwargs.get('regex'), kwargs.get('text'))[0]
    teams = kwargs.get('teams')
    week  = kwargs.get('week')

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

    line1, line2 = SlackBotLib.format_matchup(
      name1=team.team_name,
      name2=opponent.team_name,
      score1=team.scores[week-1],
      score2=opponent.scores[week-1])
    msg.append('Week %s: vs. %s (%s):\n' % (week, opponent.owner, opponent.team_name))
    msg.append('%s vs. %s:\n' % (team.owner, opponent.owner))
    msg.append('```%s\n%s```' % (line1, line2))
    return ''.join(msg)

  def _action_matchups_all(self, **kwargs):
    """
    Returns all matchups in the given week.

    Args in kwargs:
      teams:  A list of Team objects, one for each team in the league.
              See: espnff.Team

      week:   The week number of the matchup to be fetched. Note: this does NOT
              start at zero. Range: in all likelihood, 1 to 16.
    """
    msg = []
    teams = kwargs.get('teams')
    week  = kwargs.get('week')

    msg.append('Week %s matchups:\n' % week)
    for t in teams:
      opponent = t.schedule[week-1]
      line1, line2 = SlackBotLib.format_matchup(
        name1=t.team_name,
        name2=opponent.team_name,
        score1=t.scores[week-1],
        score2=opponent.scores[week-1]
        )
      msg.append('%s vs. %s:\n' % (t.owner, opponent.owner))
      msg.append('```%s\n%s```\n' % (line1, line2))
      teams.remove(opponent)

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

  # Add parsing for 'my' or move it up to SlackBot
  def _action_tell(self, **kwargs):
    """
    Returns a candid and unflattering opinion of a named player's fantasy team.

    Args in kwargs:
      regex:  The regular expression which matched the Action containing this
              method. Necessary to retrieve the name of the person who should be
              insulted.

      teams:  A list of Team objects, one for each team in the league.
              These are the teams for the CURRENT year's league.
              See: espnff.Team

      teams_prev: A list of Team objects, one for each team in the league.
                  These are the teams for the PREVIOUS year's league.
                  See: espnff.Team

      text:   The text content of the message in which the request was made.

      user:   The user whose message triggered this method. This is not necessarily
              the person whose matchup should be fetched. Their first name must
              be supplied as well, as this will be used to match a Slack user to
              a member of the fantasy league. If your league has people with the
              same first name, you may wish to change this behavior. This will
              likely be made more robust in the future.
    """
    msg = []
    team_owner = re.findall(kwargs.get('regex'), kwargs.get('text'))[0]
    teams      = kwargs.get('teams')
    teams_prev = kwargs.get('teams_prev')
    team_name       = None
    team_place_prev = None
    is_user = False

    if team_owner.lower() == 'my':
      team_owner = kwargs['user']['first_name']
      is_user = True

    for t in teams:
      if t.owner.split()[0].lower() == team_owner.lower():
        team_name = t.team_name
    for t in teams_prev:
      if t.owner.split()[0].lower() == team_owner.lower():
        team_place_prev = t.overall_standing

    if team_name:
      msg.append(team_name + ' are terrible and %s totally clueless.' % ('you are' if is_user else '%s is' % str.capitalize(team_owner)))
      if team_place_prev:
        msg.append(' %s somehow came in %s last year, but %s manage to do worse this year.' % (('You' if is_user else 'He'), self._inflect.ordinal(team_place_prev), ('you\'ll' if is_user else 'he\'ll')))
    else:
      msg.append('I don\'t know who %s is, but I bet he sucks at fantasy.' % str.capitalize(team_owner))

    return ''.join(msg)

  def _action_standings(self, **kwargs):
    """
    Returns the curren overall standings of the league.
    """
    return 'To be implemented.'
