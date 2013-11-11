#!/usr/bin/python

import argparse
import os
import pickle
import random
import sys

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--metadata_file', required=True)
  parser.add_argument('--feature_dir', required=True)
  parser.add_argument('--max_pos_count', required=True)
  parser.add_argument('--max_neg_count', required=True)
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()

  max_pos_count = int(args.max_pos_count)
  max_neg_count = int(args.max_neg_count)

  print 'Scanning feature dir for available feature points...'
  feature_files = [f for f in os.listdir(args.feature_dir)
                   if f.endswith('.pkl')]
  tds = set()
  for i in range(len(feature_files)):
    f = feature_files[i]
    fp = open('%s/%s' % (args.feature_dir, f), 'rb')
    features = pickle.load(fp)
    fp.close()
    ticker = f[:f.rfind('.')]
    for feature in features:
      date = feature[0]
      tds.add('%s %s' % (ticker, date))
    if i % 100 == 0:
      print i
      sys.stdout.flush()
  print 'Found %d feature points for %d tickers' % (
      len(tds), len(feature_files))

  print 'Loading training metadata...'
  with open(args.metadata_file, 'r') as fp:
    lines = fp.read().splitlines()
  pos, neg = [], []
  count = 0
  # Skip line 0 which records runtime flags.
  for i in range(1, len(lines)):
    d, t, l, g, r = lines[i].split(' ')
    td = '%s %s' % (t, d)
    if td not in tds:
      count += 1
      continue
    if l == '+1':
      pos.append(td)
    else:
      assert l == '-1'
      neg.append(td)
  print ('Loaded %d positive, %d negative, %d discarded (missing feature)'
         ' samples' % (len(pos), len(neg), count))

  if max_pos_count > 0 and max_pos_count < len(pos):
    random.shuffle(pos)
    pos = pos[:max_pos_count]
  if max_neg_count > 0 and max_neg_count < len(neg):
    random.shuffle(neg)
    neg = neg[:max_neg_count]
  print '%d positive, %d negative samples after filtering' % (
      len(pos), len(neg))

  # Organize features into ticker => date, date ... so that we can write output
  # in one scan of feature files.
  feature_map = dict()
  for td in pos:
    t, d = td.split(' ')
    if t not in feature_map:
      feature_map[t] = dict()
    feature_map[t][d] = '+1'
  for td in neg:
    t, d = td.split(' ')
    if t not in feature_map:
      feature_map[t] = dict()
    feature_map[t][d] = '-1'

  print 'Scanning feature dir and writing training data...'
  data_fp = open('%s/data.txt' % args.output_dir, 'w')
  meta_fp = open('%s/meta.txt' % args.output_dir, 'w')
  count = 0
  dim = None
  for ticker in feature_map.keys():
    fm = feature_map[ticker]
    fp = open('%s/%s.pkl' % (args.feature_dir, ticker), 'rb')
    features = pickle.load(fp)
    fp.close()
    for feature in features:
      if dim is not None:
        assert len(feature) == dim
      dim = len(feature)
      if feature[0] not in fm:
        continue
      label = fm[feature[0]]
      data = ['%d:%f' % (i, feature[i]) for i in range(1, len(feature))]
      meta = '%s %s' % (ticker, feature[0])
      print >> data_fp, '%s %s' % (label, ' '.join(data))
      print >> meta_fp, meta
    if count % 100 == 0:
      print count
      sys.stdout.flush()
    count += 1
  data_fp.close()
  meta_fp.close()

if __name__ == '__main__':
  main()

