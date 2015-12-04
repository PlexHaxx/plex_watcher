#!/usr/bin/env python

import argparse
import json
import logging
import os
import ssl
import sys
import urllib2

PATH = os.path.dirname(os.path.realpath(__file__))
xmltodict_path = os.path.join(PATH, 'xmltodict')
sys.path.append(xmltodict_path)

import xmltodict


def GetStatus(ip, port):
  status_xml = ''
  url = 'https://%s:%s/status/sessions' % (ip, port)
  context = ssl._create_unverified_context()
  request = urllib2.urlopen(url, context=context)
  response = request.read()
  return xmltodict.parse(response, dict_constructor=dict)['MediaContainer']


def ParseItem(data):
  if '@grandparentTitle' in data:
    artist = '%s - ' % data['@grandparentTitle']
  else:
    artist = ''
  try:
    title = artist + data['@title']
    user = data['User']['@title']
    player = data['Player']['@title']
  except:
    user = ''
    title = ''
    player = ''
  return '%s is accessing %s on %s' % (user, title, player)


def ParseData(data):
  stats = []
  for k in ['Video', 'Track']:
    if k in data:
      v = data[k]
      if type(v) == list:
        for i in v:
          stats.append(ParseItem(i))
      else:
        stats.append(ParseItem(v))
  return stats


def ReadStats(stats_file):
  try:
    with open(stats_file) as f:
      stats = json.load(f)
  except:
    stats = []
  return stats


def WriteStats(stats, stats_file):
  with open(stats_file, 'w') as f:
    json.dump(stats, f)


def UpdateStats(old_stats, cur_stats):
  new_stats = []
  for i in cur_stats:
    if i not in old_stats:
      new_stats.append(i)
  return new_stats


def Main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--ip', default='10.0.0.2',
                      help='the ip of the plex server')
  parser.add_argument('-p', '--port', default=32400,
                      help='the port plex is running on')
  args = parser.parse_args()

  logFormatter = logging.Formatter('%(asctime)s  %(message)s',
                                   datefmt='%m-%d %H:%M:%S')

  rootLogger = logging.getLogger()
  rootLogger.setLevel(logging.DEBUG)
  fileHandler = logging.FileHandler('/var/log/plex_watcher.log')
  fileHandler.setFormatter(logFormatter)
  rootLogger.addHandler(fileHandler)

  data = GetStatus(args.ip, args.port)
  old_stats = ReadStats('%s/stats.json' % PATH)
  cur_stats = ParseData(data)
  new_stats = UpdateStats(old_stats, cur_stats)
  if cur_stats != old_stats:
    WriteStats(cur_stats, '%s/stats.json' % PATH)
  if len(new_stats) != 0:
    for line in new_stats:
      logging.info(line)


if __name__ == "__main__":
  Main()
