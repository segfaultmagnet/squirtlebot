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
          for a in self.keywords['match']:
            if self.keywords['match'][a].match(o['text']):
              result['action'] = a

          # Look for everything else.
          if result['action'] == None:
            for a in self.keywords['search']:
              if self.keywords['search'][a].search(o['text']):
                result['action'] = a

          # Return the relevant parts of this activity.
          if result['action']:
            result['blob']          = TextBlob(o['text'])
            result['channel']['id'] = o['channel']
            result['user']['id']    = o['user']
            result['channel']['name'] = self.get_channel_name(result['channel']['id'])
            result['user']['name']    = self.get_user_name(result['user']['id'])
          return result

    return result


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
