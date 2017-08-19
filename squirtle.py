#!/usr/bin/env python3
"""Usage:
  squirtle.py [-d] <config>
  squirtle.py -h | --help
  squirtle.py -v | --version

Arguments:
  config        A JSON file containing configuration options.

Options:
  -d --debug    Change logging level to DEBUG.
  -h --help     Show this help message.
  -v --version  Display program version number.
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

import os
import sys
import json
import logging
import re
import time

from docopt import docopt

from slackbot import SlackBot, SquirtleBot

def _assert_config(config):
  for b in config:
    assert config[b]['API Token'] != 'changeme', "Change \'API Token\' from default: %r" % config[b]['API Tken']
    assert config[b]['League ID'] != 12345, "Change \'League ID\' from default: %r" % config[b]['League ID']
    assert config[b]['League Year'] != 12345, "Change \'League Year\' from default: %r" % config[b]['League Year']

def _main(bots, logger):
  config_all = {}
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
      config_all.update(b.config_file())
      b.stop()
    print('Done.')

  return config_all

def __init__(args):
  root = os.path.abspath(os.path.dirname(__file__))
  assert os.path.isfile(args['<config>']), "Configuration file %r not found." % repr(args['<config>'])
  DEBUG = args['--debug']

  config = None
  with open(os.path.relpath(args['<config>'], start=root), 'r') as file:
    config = json.load(file)
  _assert_config(config)

  level = logging.INFO
  if DEBUG:
    level = logging.DEBUG
  
  logger = logging.getLogger(str(__name__))
  logger.setLevel(level)
  handler = logging.FileHandler(
    os.path.relpath(
      'logs/' + os.path.basename(__file__).split('.')[0] + '.log'))
  handler.setFormatter(
    logging.Formatter(
      fmt='%(asctime)s %(module)s: %(funcName)s(%(lineno)s) %(levelname)s: %(message)s',
      datefmt='%Y/%m/%d %H:%M:%S'))
  logger.addHandler(handler)

  bots  = []

  for b in config:
    name = b
    botconfig = config[b]
    botconfig['Dat_dir'] = 'dat'
    botconfig['Logger']  = logger.getChild(name)
    botconfig['Logger'].setLevel(level)
    botconfig['Root']    = root
    bots.append(globals()[botconfig['Type']](name, botconfig, debug=DEBUG))

  config_all = _main(bots, logger)
  with open(os.path.relpath(args['<config>'], start=root), 'w') as file:
    json.dump(config_all, file, sort_keys=True, indent=2)

if __name__ == '__main__':
  __init__(docopt(__doc__, help=True, version=__version__))
  sys.exit()
