"""
import sys
import re

sys.path.append('..')

from nose.tools import with_setup
from slackbot.actionhandler import ActionHandler

def parse_and_exec_test():
  ah = ActionHandler(name='test_case')

  args = {
    'text': ''
  }
  parsed = ah.parse_keywords(**args)
  assert parsed == None

  ah.exec_action()
  assert 

  args = {
    'text': 'barry manilow ansegFaultmaGnetd bark'
  }
  parsed = ah.parse_keywords(**args)
  assert parsed == {'about:author': 'barry manilow and bark'}
"""
