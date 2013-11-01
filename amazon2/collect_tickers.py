#!/usr/bin/python

import argparse
import os

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_dir', required=True)
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()

  tickers = [f[:f.rfind('.')] for f in os.listdir(args.data_dir)
             if f.endswith('.csv')]
  with open(args.output_file, 'w') as fp:
    for ticker in sorted(tickers):
      print >> fp, ticker

if __name__ == '__main__':
  main()

