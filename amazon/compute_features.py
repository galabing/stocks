#!/usr/local/bin/python3

import argparse
import math
import os
import pickle

PRICE_BONUS = 0.01
VOLUME_BONUS = 1.0
EPS = 0.01

def compute_derivatives(v, bonus):
  return [(v[i+1]-v[i])/(v[i]+bonus) for i in range(len(v)-1)]

def normalize(v):
  m = sum(v)/len(v)
  n = [x - m for x in v]
  l = math.sqrt(sum([x*x for x in n]))
  if l > EPS:
    n = [x/l for x in n]
  return n

def compute_features(dpv, j, step, num):
  offset = step*(num-1)
  assert j >= offset
  p = [dpv[i][1] for i in range(j-offset, j+1, step)]
  v = [dpv[i][2] for i in range(j-offset, j+1, step)]
  assert len(p) == num
  assert len(v) == num
  dp = compute_derivatives(p, PRICE_BONUS)
  dv = compute_derivatives(v, VOLUME_BONUS)
  assert len(dp) == num - 1
  assert len(dv) == num - 1
  return normalize(p) + normalize(v) + normalize(dp) + normalize(dv)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--data_dir', required=True)
  parser.add_argument('--step', required=True)
  parser.add_argument('--num', required=True)
  parser.add_argument('--feature_dir', required=True)
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  step = int(args.step)
  num = int(args.num)
  assert step > 0
  assert num > 0
  offset = step*(num-1)

  for i in range(len(tickers)):
    ticker = tickers[i]
    print('Processing %d/%d: %s' % (i+1, len(tickers), ticker))
    input_file = '%s/%s.txt' % (args.data_dir, ticker)
    if not os.path.isfile(input_file):
      print('!! %s does not exist, skipping' % input_file)
      continue
    with open(input_file, 'r') as fp:
      lines = fp.read().splitlines()
    if len(lines) < offset:
      print('!!! not enough data for %s, skipping' % ticker)
      continue
    dpv = []
    for line in lines:
      d, p, v = line.split(' ')
      dpv.append([d, float(p), float(v)])
    output = []
    for j in range(offset, len(dpv)):
      features = compute_features(dpv, j, step, num)
      assert len(features) == num*2 + (num-1)*2
      output.append([dpv[j][0]] + features)
    output_file = '%s/%s.p' % (args.feature_dir, ticker)
    fp = open(output_file, 'wb')
    pickle.dump(output, fp, 1)
    fp.close()

if __name__ == '__main__':
  main()

