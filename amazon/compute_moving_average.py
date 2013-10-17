#!/usr/local/bin/python3

import argparse
import os

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--k', default='5')
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  k = int(args.k)
  assert k > 0
  for i in range(len(tickers)):
    ticker = tickers[i]
    print('Processing %d/%d: %s' % (i+1, len(tickers), ticker))
    input_file = '%s/%s.txt' % (args.input_dir, ticker)
    if not os.path.isfile(input_file):
      print('!! %s does not exist, skipping' % input_file)
      continue
    with open(input_file, 'r') as fp:
      lines = fp.read().splitlines()
    dpv = []
    for line in lines:
      d, p, v = line.split(' ')
      dpv.append([d, float(p), float(v)])
    output_file = '%s/%s.txt' % (args.output_dir, ticker)
    with open(output_file, 'w') as fp:
      for j in range(len(dpv)):
        p = sum([x[1] for x in dpv[max(0,j-k+1):j+1]])/(min(j+1,k))
        v = sum([x[2] for x in dpv[max(0,j-k+1):j+1]])/(min(j+1,k))
        print('%s %.2f %.2f' % (dpv[j][0], p, v), file=fp)

if __name__ == '__main__':
  main()

