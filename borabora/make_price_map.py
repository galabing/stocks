#!/usr/local/bin/python3

import argparse
import os
import utils

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--data_dir', required=True)
  parser.add_argument('--min_date', default='0000-00-00')
  parser.add_argument('--max_date', default='9999-99-99')
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  print('processing %d tickers' % len(tickers))

  print('loading price map from raw data...')
  price_map = utils.read_price_map_from_files(tickers, args.data_dir, min_date=args.min_date, max_date=args.max_date)
  print('done, %d entries in the price map' % len(price_map))

  utils.write_price_map(price_map, args.output_file)

if __name__ == '__main__':
  main()

