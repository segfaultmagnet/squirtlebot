# Name:         logger.py
# Authors:      Matthew Sheridan
# Date:         05 August 2017
# Revision:     08 August 2017
# Copyright:    Matthew Sheridan 2017
# Licence:      Beer-Ware License Rev. 42


__author__  = 'Matthew Sheridan'
__credits__ = ['Matthew Sheridan']
__date__    = '08 August 2017'
__version__ = '0.1'
__status__  = 'Development'


import os
import time
import threading

from collections import deque


class Logger(threading.Thread):
  DAYS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  def __init__(self, logdir):
    super(Logger, self).__init__()

    self._lock     = threading.Lock()
    self._logpath  = self.get_log_filename(logdir)
    self._msgqueue = deque()
    self._run      = True


  def run(self):
    while self._run or len(self._msgqueue) > 0:
      try:
        chunk = ''

        while len(self._msgqueue) > 0:
          chunk += Logger.timestamp() + self._msgqueue.popleft() + '\n'
        
        if len(chunk) > 0:
          self.writechunk(chunk)

      except IndexError:
        pass
      time.sleep(1)


  def stop(self):
    self._run = False


  def add(self, msg):
    """ Queues the given message for writing to file. """
    if self._run:
      self._msgqueue.append(msg)


  def writechunk(self, chunk):
    """ Writes the given chunk to file. """
    try:
      if self._lock.acquire(blocking=True, timeout=10):
        with open(self._logpath, 'a+') as log:
          log.write(chunk)
          self._lock.release()
    except IndexError:
      raise


  def get_log_filename(self, logdir):
    curr = time.localtime()
    logname = logdir + '/log_' + str(curr.tm_year)         \
              + Logger.int_to_str(curr.tm_mon, 2)          \
              + Logger.int_to_str(curr.tm_mday, 2) + '_'   \
              + Logger.int_to_str(curr.tm_hour, 2)         \
              + Logger.int_to_str(curr.tm_min, 2) + '_'    \
              + Logger.int_to_str(curr.tm_sec, 2) + '.txt'
    return os.path.normpath(logname)


  def int_to_str(int, figs):
    """
    Returns int as a string, aligned to the right; i.e. a string of at least
    length fig containing spaces in front of the value of int.
    """
    string = str(int)
    while len(string) < figs:
      string = '0' + string
    return string


  def timestamp():
    """
    Returns string of the local time formatted for logging.
    """
    curr = time.localtime()
    stamp = '[' + Logger.int_to_str(curr.tm_mday, 2)   \
            + Logger.DAYS[curr.tm_wday]                \
            + str(curr.tm_year)[2:]                    \
            + ' ' + Logger.int_to_str(curr.tm_hour, 2) \
            + ':' + Logger.int_to_str(curr.tm_min, 2)  \
            + '] '

    return stamp
