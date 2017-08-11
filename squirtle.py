#!/usr/bin/python3

# Name:         squirtle.py
# Authors:      Matthew Sheridan
# Date:         04 August 2017
# Revision:     08 August 2017
# Copyright:    Matthew Sheridan 2017
# Licence:      Beer-Ware License Rev. 42

"""
Usage:
  squirtle.py <config>
  squirtle.py -h | --help
  squirtle.py -v | --version

Arguments:
  config         A JSON file containing configuration options.

Options:
  -h --help      Show this help message.
  -v, --version  Display program version number.
"""


__author__  = 'Matthew Sheridan'
__credits__ = ['Matthew Sheridan']
__date__    = '08 August 2017'
__version__ = '0.1'
__status__  = 'Development'


import os
import sys
import json
import re
import time

from types import *

from docopt import docopt

from logger.logger import Logger
from slackbot import SlackBot


def _assert_config(config):
  assert type(config['Debug']) is bool, "\'Debug\'' is not bool: %r" % config['Debug']

  for b in config['Bots']:
    assert config['Bots'][b]['API_token'] != 'changeme', "Change \'API_token\' from default: %r" % config['Bots'][b]['API_token']


def _main(bots, logger):
  for b in bots:
    b.start()

  try:
    while True:
      time.sleep(1)
      cont = False
      for b in bots:
        if b.stopped() == False:
          cont = True
      if cont == False:
        break

  except KeyboardInterrupt as k:
    print('Stopping all bots.')
  finally:
    for b in bots:
      b.stop()
    logger.stop()
    print('Done.')


def __init__(args):
  root = os.path.abspath(os.path.dirname(__file__))
  assert os.path.isfile(args['<config>']), "Configuration file %r not found." % repr(args['<config>'])

  config = None
  with open(os.path.relpath(args['<config>'], start=root), 'r') as file:
    config = json.load(file)

  _assert_config(config)

  logger = Logger(os.path.relpath(config['Log_dir'], start=root))
  logger.start()
  debug  = config['Debug']

  bots  = []

  for b in config['Bots']:
    name = b
    botconfig = config['Bots'][b]
    botconfig['Dat_dir'] = config['Dat_dir']
    botconfig['Logger']  = logger
    botconfig['Root']    = root

    if re.search('testing', name, flags=re.I):
      debug = True

    bots.append(SlackBot(name, botconfig, debug=debug))

  _main(bots, logger)


if __name__ == '__main__':
  __init__(docopt(__doc__, help=True, version=__version__))
  sys.exit()
