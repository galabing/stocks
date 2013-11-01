#!/usr/local/bin/python3

""" Downloads csv files of historical stock data from yahoo finance.
"""

import argparse
import os

WGET = '/usr/local/bin/wget'

def download(ticker, output_path):
  url = ('http://ichart.finance.yahoo.com/table.csv?s=%s'
         % ticker.replace('.', '-'))
  cmd = '%s -q "%s" -O %s' % (WGET, url, output_path)
  if os.system(cmd) != 0:
    print('Download failed for %s: %s' % (ticker, url))
    if os.path.isfile(output_path):
      os.remove(output_path)
    return False
  assert os.path.isfile(output_path)
  return True

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--overwrite', action='store_true')
  args = parser.parse_args()

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  print('Processing %d tickers' % len(tickers))

  sl, fl = [], []  # Lists of tickers succeeded/failed to download.
  for i in range(len(tickers)):
    ticker = tickers[i]
    print('%d/%d: %s' % (i+1, len(tickers), ticker))

    output_path = '%s/%s.csv' % (args.output_dir, ticker.replace('^', '_'))
    dl = False
    if os.path.isfile(output_path):
      action = 'skipping'
      if args.overwrite:
        os.remove(output_path)
        action = 'overwriting'
        dl = True
      print('Output file exists: %s, %s' % (output_path, action))
    else: dl = True

    if dl:
      ok = download(ticker, output_path)
      if ok: sl.append(ticker)
      else: fl.append(ticker)
  print('Downloaded %d tickers, failed %d tickers'
        % (len(sl), len(fl)))
  print('%d downloaded tickers' % len(sl))
  print('%d failed tickers: %s' % (len(fl), fl))

if __name__ == '__main__':
  main()

