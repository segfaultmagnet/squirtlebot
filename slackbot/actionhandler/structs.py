__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

"""
Provides simple classes to abstract regular expressions (Keywords) and the
functions (Actions) that should be called when found in parsed text.
"""

import re

class Action(object):
  """
  Args:
    name:   a string that will be used to identify this Action when one or more
            Keywords are matched

    func:   a function which should be called when this Action is matched
  """
  def __init__(self, name, func):
    self.name = name.lower()
    self.func = func

  def __eq__(self, other):
    return self.name == other.name \
           and self.func == other.func

  def __repr__(self):
    return str('Action(name=%s,func=%r)' % (self.name, self.func))

  def __str__(self):
    return self.name


class Keyword(object):
  """
  Args:
    name:     a string that will be used to identify this Keyword and match it
              to Action(s) which should be called

    regex:    a compiled regular expression

    re_match: boolean; True if the regex should only be used to match from the
              beginning (left) of a string, as in re.match()
  """
  def __init__(self, name, regex, re_match=False):
    self.name = name.lower()
    self.regex = regex
    self.re_match = re_match

  def __eq__(self, other):
    return self.name == other.name \
           and self.regex == other.regex           \
           and self.re_match == other.re_match

  def __repr__(self):
    return str('Keyword(name=%s,regex=%r,re_match=%r)' % (self.name, self.regex, self.re_match))

  def __str__(self):
    return self.name
