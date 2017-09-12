"""
Defines the specific behavior of a bot. This class can be used to search text
for specific keywords or regular expressions, returning a Keyword indicating
the type of response to be given. It also provides definitions for those
responses and a method for executing them on behalf of the bot.
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

import re

import inflect

from .structs import Action, Keyword
from ..slackbotlib import SlackBotLib

class ActionHandler(object):
  def __init__(self, name, at):
    """
    Args:
      name:   A string containing this bot's name. May be used by the bot to
              identify text relevant to itself.

      at:     String representation of a Slack bot's @BotName identifier. This
              is not a traditional name like 'SlackBot', but rather is of the
              format '<@ABCD123>' or similar, containing an assortment of
              alphanumeric characters.
    """
    self.at = at
    self.name = name
    self._actions  = [
      Action(name='about:author', function=self._action_about_author),
      Action(name='about:bot', function=self._action_about_bot),
      Action(name='help', function=self._action_help)
    ]
    self._keywords = [
      Keyword(
        name='about:author',
        regex=re.compile('(?:about|who is) (?:%s|%s)' % (__author__, __email__.split('@')[0]), flags=re.I),
        name_pretty='About the author',
        examples=['Who is %s?' % __author__]
      ),
      Keyword(
        name='about:bot', 
        regex=re.compile('(?:about|who is) (?:SquirtleBot|%s|%s)' % (self.name, self.at), flags=re.I),
        name_pretty='About the bot', 
        examples=['Who is %s?' % self.at]
      ),
      Keyword(
        name='help', 
        regex=re.compile('(?:%s|%s) help' % (self.name, self.at)),
        name_pretty='Help',
        examples=['%s help' % self.at],
        re_match=True
      ),
    ]

  def exec_action(self, **kwargs):
    """
    Executes the function specified by one or more Actions given as an argument,
    but does not execute any further actions, only returning what those functions
    themselves return.

    Args:
      action: Action(s) matching one of the Actions listed in self._actions;
              this is the Action to be executed. Other args needed for that
              Action's own arguments are passed through.

    Returns:  Executes the methods specified by those Actions and returns their
              result, if any.
    """
    action_name = kwargs.get('action')
    execute = [a for a in self._actions if a.name == action_name]
    result = []
    for e in execute:
      result.append(e.function(**kwargs))
    return result

  def parse_keywords(self, **kwargs):
    """
    Compares regular expressions in Keywords to the given text and returns the
    name of that Keyword if a match is found.
    """
    text    = kwargs.get('text')
    execute = {}

    if text:
      for k in self._keywords:
        if (k.re_match and k.regex.match(text))        \
          or (not k.re_match and k.regex.search(text)):
            execute[k.name] = k.regex
    if execute == {}:
      return None
    return execute

  def update(self, actions=None, keywords=None):
    """
    Merges new lists of Actions and Keywords with the existing lists. New entries
    are placed at the front of the list (worth noting for help message purposes).
    """
    for a in self._actions:
      if not a in actions:
        actions.append(a)
    self._actions = actions

    for k in self._keywords:
      if not k in keywords:
        keywords.append(k)
    self._keywords = keywords

  def help_string(keyword):
    lines = []
    if keyword.name_pretty() != None and keyword.examples != None:
      lines.append('%s:' % keyword.name_pretty())

      example_strings = []
      for e in keyword.examples:
        example_strings.append('%s' % e)

      lines.append('```%s```' % '\n'.join(example_strings))
      lines.append('')

    return '\n'.join(str(l) for l in lines)

  """
  The following are methods which should be executed when an Action is called
  (see the Action instances above in self._actions). If the SlackBot should post
  a message to the channel that prompted the Action, that message should be
  returned by these methods.
  """

  def _action_about_author(self, **kwargs):
    return(__author__ + ' is the author of this bot. Please visit %r!' % __website__)

  def _action_about_bot(self, **kwargs):
    return('%s is a chatbot created by %s. Please visit %r!' % (self.name, __author__, __website__))

  def _action_help(self, **kwargs):
    """ Returns a help message with examples of each command (where provided). """
    msg = []
    for k in self._keywords:
      msg.append(ActionHandler.help_string(k))
    return ''.join(msg)
