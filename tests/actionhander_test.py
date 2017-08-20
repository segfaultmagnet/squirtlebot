import sys
import re

sys.path.append('..')

from nose.tools import with_setup
from slackbot.actionhandler import ActionHandler

"""
def setup():
  ah = ActionHandler(name='test_case', at='<@ABC123>')

@with_setup(setup)
def parse_and_exec_test():
  args = {
    'text': ''
  }
  parsed = ah.parse_keywords(**args)
  assert parsed == None

  ah.exec_action()
  # assert 

  args = {
    'text': 'barry manilow ansegFaultmaGnetd bark'
  }
  parsed = ah.parse_keywords(**args)
  for k in parsed:
    assert k == 'about:author'
"""
