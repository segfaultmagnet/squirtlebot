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

class ActionHandler(object):
  def __init__(self, name, at):
    self.at = at
    self.name = name
    self._actions  = [
      Action(name='about:author', func=self._action_about_author),
      Action(name='about:bot', func=self._action_about_bot)
    ]
    self._keywords = [
      Keyword(name='about:author', regex=re.compile(__email__.split('@')[0], flags=re.I)),
      Keyword(name='about:author', regex=re.compile(__author__, flags=re.I)),
      Keyword(name='about:bot', regex=re.compile('about:' + name, flags=re.I), re_match=True)
    ]

  def exec_action(self, **kwargs):
    action_name = kwargs.get('action')
    execute = [a for a in self._actions if a.name == action_name]
    result = []
    for e in execute:
      result.append(e.func(**kwargs))
    return result

  def parse_keywords(self, **kwargs):
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
    for a in actions:
      if not a in self._actions:
        self._actions.append(a)

    for k in keywords:
      if not k in self._keywords:
        self._keywords.append(k)

  def _action_about_author(self, **kwargs):
    return(__author__ + ' is the author of this bot. Please visit %s!' % repr(__website__))

  def _action_about_bot(self, **kwargs):
    return('%s is a chatbot created by %s. Please visit %s!' % (name, __author__, __website__))
