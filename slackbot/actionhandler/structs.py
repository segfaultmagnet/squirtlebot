"""
Provides simple classes to abstract regular expressions (Keywords) and the
functions (Actions) that should be called when found in parsed text.
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

class Action(object):
  """
  Used to specify a SlackBot method or other function which should be called
  upon some condition as specified by one or more Keywords.
  i.e. This is a container for a function and a keyword used to trigger it.
  """
  def __init__(self, name, function):
    """
    Args:
      name:   a string that will be used to identify this Action when one or more
              Keywords are matched

      func:   a function which should be called when this Action is matched
    """
    self.name = name.lower()
    self.function = function

  def __eq__(self, other):
    return self.name == other.name \
           and self.function == other.function

  def __repr__(self):
    return str('Action(name=%s,func=%r)' % (self.name, self.function))

  def __str__(self):
    return self.name


class Keyword(object):
  """
  Specifies a regular expression which will be used in parsing text from Slack
  channels, as well as a 'name' keyword used to connect that regex to one or
  more Actions. If the regex matches text, Actions containing the same keyword
  will have their specified 'function' called.
  """
  def __init__(self, name, regex, name_pretty=None, examples=None, re_match=False):
    """
    Args:
      name:     A string that will be used to identify this Keyword and match it
                to Action(s) which should be called.

      name_pretty:  A string that can be used as a user-friendly way to identify
                    this Keyword when printed as part of a help message. This can
                    be just a title or a short blurb describing the phrase that
                    this Keyword will be matched against. If not provided, this
                    Keyword should not be shown when printed as part of a help
                    message.

      regex:    A compiled regular expression.

      examples: A list of strings that can be printed as part of a help text.
                These should be examples of the phrase being matched, and should
                be useful and informative for the end user, not just developers.
                If not provided, this Keyword should not be shown when printed as
                part of a help message.
                e.g. 'who is %s' % self.name
                e.g. '%s show Albert's matchup' % self.at

      re_match: boolean; True if the regex should only be used to match from the
                beginning (left) of a string, as in re.match();
                False, any match at any place in that string, as in re.search().
    """
    self.name = name.lower()
    self._name_pretty = name_pretty
    self.regex = regex
    self.examples = examples
    self.re_match = re_match

  def __eq__(self, other):
    return self.name == other.name             \
           and self.regex == other.regex       \
           and self.re_match == other.re_match

  def __repr__(self):
    return str('Keyword(name=%s,regex=%r,re_match=%r)' % (self.name, self.regex, self.re_match))

  def __str__(self):
    return self.name

  def name_pretty(self):
    if self._name_pretty:
      return str.capitalize(self._name_pretty)

    return None
