#!/usr/bin/python

import argparse

SECINDS = [
    'Basic Materials', 'Conglomerates', 'Consumer Goods', 'Financial',
    'Healthcare', 'Industrial Goods', 'Services', 'Technology', 'Utilities']

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_file', required=True)
  parser.add_argument('--meta_file', required=True)
  parser.add_argument('--secind_file', required=True)
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()

  secind_map = dict()
  for i in range(len(SECINDS)):
    features = [0.0 for j in range(len(SECINDS))]
    features[i] = 1.0
    secind_map[SECINDS[i]] = features
  default_features = [0.0 for j in range(len(SECINDS))]

  with open(args.secind_file, 'r') as fp:
    lines = fp.read().splitlines()
  ticker_map = dict()
  for line in lines:
    ticker, secind, _ = line.split('|')
    ticker_map[ticker] = secind

  with open(args.meta_file, 'r') as fp:
    lines = fp.read().splitlines()
  meta_keys = []
  for line in lines:
    ticker, date = line.split(' ')
    meta_keys.append(ticker)

  ifp = open(args.data_file, 'r')
  ofp = open(args.output_file, 'w')

  index = 0
  n = None
  default_count = 0
  while True:
    line = ifp.readline()
    if line == '':
      break
    assert line.startswith('+1 ') or line.startswith('-1 ')
    assert line.endswith('\n')
    label = line[:2]
    items = line[3:-1].split(' ')
    if n is None:
      n = len(items)
    else:
      assert n == len(items)
    values = []
    for i in range(n):
      k, v = items[i].split(':')
      assert int(k) == i+1
      values.append(float(v))
    meta_key = meta_keys[index]
    if meta_key in ticker_map:
      values.extend(secind_map[ticker_map[meta_key]])
    else:
      values.extend(default_features)
      default_count += 1
    assert len(values) == n + len(SECINDS)
    print >> ofp, '%s %s' % (
        label,
        ' '.join(['%d:%f' % (i+1, values[i]) for i in range(len(values))]))
    index += 1

  assert index == len(meta_keys)

  ifp.close()
  ofp.close()

  print '%d tickers used default values' % default_count

if __name__ == '__main__':
  main()

