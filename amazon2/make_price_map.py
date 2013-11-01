#!/usr/bin/python

import argparse
import os
import pickle

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--data_dir', required=True)
  parser.add_argument('--min_date', required=True)
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  price_map = dict()

  count = 0
  for i in range(len(tickers)):
    ticker = tickers[i]
    print 'Processing %d/%d: %s' % (i+1, len(tickers), ticker)
    input_file = '%s/%s.txt' % (args.data_dir, ticker)
    if not os.path.isfile(input_file):
      print '!! Input file does not exist, skipping: %s' % ticker
      continue
    with open(input_file, 'r') as fp:
      lines = fp.read().splitlines()
    for line in lines:
      d, p, v = line.split(' ')
      if d < args.min_date:
        continue
      if d not in price_map:
        price_map[d] = { ticker: float(p) }
      else:
        price_map[d][ticker] = float(p)
      count += 1

  fp = open(args.output_file, 'wb')
  pickle.dump(price_map, fp, 1)
  fp.close()

  print 'Price map contains %d entries, %d elements' % (len(price_map), count)

if __name__ == '__main__':
  main()

