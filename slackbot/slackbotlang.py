__author__     = 'Matthew Sheridan'
__copyright__  = 'Copyright 2017, Matthew Sheridan'
__license__    = 'Beer-Ware License Rev. 42'
__maintainer__ = 'Matthew Sheridan'
__email__      = 'segfaultmagnet@gmail.com'
__website__    = 'https://github.com/segfaultmagnet'
__credits__    = ['Matthew Sheridan']
__version__    = '0.1'
__status__     = 'Development'

import os
import re

import _pickle as pickle

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
    tags = []
    for t in blob.tags:
      tags.append('\n  ' + repr(t))
    self.dbg('tags: ' + ''.join(tags))

    noun_phrases = []
    for n in blob.noun_phrases:
      noun_phrases.append('\n  ' + repr(n))
    self.dbg('noun phrases: ' + ''.join(noun_phrases))

    words = []
    for w in blob.words:
      words.append('\n  ' + repr(w))
    self.dbg('words: ' + ''.join(words))

    sentences = []
    for s in blob.sentences:
      sentences.append('\n  ' + repr(s))
    self.dbg('sentences: ' + ''.join(sentences))

    self.dbg('sentiment:\n  polarity: ' + str(blob.sentiment.polarity)
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
