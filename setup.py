#!/usr/bin/env python

from setuptools import setup, find_packages

readme = 'README.md'

with open('LICENSE') as f:
  license = f.read()

try:
  from pypandoc import convert
  read_md = lambda f: convert(f, 'rst')
except ImportError:
  print("Module 'pypandoc' not found.")
  read_md = lambda f: open(f, 'r').read()

setup(
  name='squirtlebot',
  version='0.1',
  description='Sassy fantasy football chatbot for Slack',
  long_description=read_md(readme),
  author='Matthew Sheridan',
  author_email='segfaultmagnet@gmail.com',
  url='https://github.com/segfaultmagnet',
  license=license,
  packages=find_packages(exclude=('tests', 'docs')),
  install_requires=[
    'docopt',
    'espnff',
    'inflect',
    'lxml',
    'markovify',
    'slackclient',
    'textblob'
  ]
)
