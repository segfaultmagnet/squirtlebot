# Name:         slackbotlang.py
# Authors:      Matthew Sheridan
# Date:         05 August 2017
# Revision:     08 August 2017
# Copyright:    Matthew Sheridan 2017
# Licence:      Beer-Ware License Rev. 42


__author__  = 'Matthew Sheridan'
__credits__ = ['Matthew Sheridan']
__date__    = '05 August 2017'
__version__ = '0.1'
__status__  = 'Development'


import os
import re

import _pickle as pickle

from textblob import TextBlob
from textblob.classifiers import NaiveBayesClassifier


class SlackBotLang:
  _classifier      = None
  _classifier_path = None


  def init_classifier(self):
    self._classifier = self.read_classifier(self._classifier_path)

    if not self._classifier:
      self._classifier = NaiveBayesClassifier(self.train_classifier_temp())

    try:
      self.write_classifier(self._classifier, self._classifier_path)
    except:
      raise


  def parse_commands(self, text):
    """
    Scan text for command phrase.

    Returns:
      The command found, if any.

      The original text stripped of the command phrase.
    """
    cmd     = None
    newtext = ''
    for c in self.commands:
      r = self.commands[c]
      if r.match(text):
        newtext = re.sub(r, '', text, count=1)
        cmd = c
    return cmd, newtext


  def parse_keywords(self, text):
    """ Scan text for keywords with pre-defined responses. """
    keywd = None
    for k in self.keywords['match']:
      if self.keywords['match'][k].match(text):
        keywd = k

    # Look for everything else.
    if keywd == None:
      for k in self.keywords['search']:
        if self.keywords['search'][k].search(text):
          keywd = k

    return keywd


  def parse_rtm(self, output):
    """
    Returns: if this bot is mentioned, a dict containing:
               a TextBlob of the message
               the channel in which it was sent
               the user who sent it
    """
    result = {'action': None,
              'blob': None,
              'channel': {'name': None, 'id': None},
              'user': {'name': None, 'id': None}}
    local_output = output

    if local_output and len(local_output) > 0:
      for o in local_output:
        if o and 'text' in o and o['user'] != self.id():
          
          # Scan text for keywords with pre-defined responses.
          action = self.parse_keywords(o['text'])
          if action:
            result['action'] = action

          # Return the relevant parts of this activity.
          if result['action']:
            result['blob']          = TextBlob(o['text'])
            result['channel']['id'] = o['channel']
            result['user']['id']    = o['user']
            result['channel']['name'] = self.get_channel_name(result['channel']['id'])
            result['user']['name']    = self.get_user_name(result['user']['id'])
          return result

    return result


  def set_commands(self):
    """
    Keywords for which the bot should execute specific commands; these follow
    @bot mentions.
    """
    self.commands = {
      'opinion':      re.compile('(what do you think|what\'s your opinion|what is your opinion) (of|about)', flags=re.I),
      'say':          re.compile('say( that)*', flags=re.I),
      'tell':         re.compile('tell me about', flags=re.I)
    }


  def set_keywords(self):
    """
    Keywords for which the bot should return pre-defined responses, including
    @bot mentions.
    """
    self.keywords = {
      'search': {
        'brady':      re.compile('brady', flags=re.I),
        'buttfumble': re.compile('fumble', flags=re.I),
        'geno':       re.compile('[g]+[e]+[n]+[o]+', flags=re.I),
        'jets':       re.compile('[j]+[-]*[e]+[-]*[t]+[-]*[s]+', flags=re.I),
        'mention':    re.compile(str(self.at())),
      },
      'match': {
        'at_bot':     re.compile(str(self.at()), flags=re.I),
      }}


  def read_classifier(self, path):
    """ Reads and returns an existing NaiveBayesClassifier from file. """
    classifier = None
    try:
      assert os.path.isfile(path), "No classifier found: %r" % repr(path)
      with open(path, 'rb') as c:
        classifier = pickle.load(c)
    except AssertionError:
      return None
    return classifier


  def write_classifier(self, classifier, path):
    """ Writes the given NaiveBayesClassifier to file. """
    with open(path, 'wb') as c:
      pickle.dump(classifier, c)


  def dump_blob(self, blob):
    tags = ''
    for t in blob.tags:
      tags += '\n  ' + repr(t)
    self.log('tags: ' + tags)

    noun_phrases = ''
    for n in blob.noun_phrases:
      noun_phrases += '\n  ' + repr(n)
    self.log('noun phrases: ' + noun_phrases)

    words = ''
    for w in blob.words:
      words += '\n  ' + repr(w)
    self.log('words: ' + words)

    sentences = ''
    for s in blob.sentences:
      sentences += '\n  ' + repr(s)
    self.log('sentences: ' + sentences)

    self.log('sentiment:\n  polarity: ' + str(blob.sentiment.polarity)
             + '\n  subjectivity: ' + str(blob.sentiment.subjectivity))


  def train_classifier_temp(self):
    train = [
      ('The Patriots are hot garbage', 'patriots'),
      ('Tom Brady sucks', 'patriots'),
      ('Tom Brady is a big fat cheater', 'patriots'),
      ('Ryan Fitzpatrick is a bad quarterback', 'jets'),
      ('Mark Sanchez fumbles the ball often', 'jets'),
      ('Geno Smith is just plain terrible', 'jets'),
      ('butt fumble', 'jets')
    ]
    return train
