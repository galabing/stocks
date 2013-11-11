#!/usr/bin/python

import argparse
import math
import os
import pickle

PRICE_BONUS = 0.01
VOLUME_BONUS = 1.0

TEST = False

def compute_features(dpv, offset, step, num):
  buff = step*(num-1)
  assert offset >= buff
  p = [dpv[i][1] for i in range(offset-buff, offset+1)]
  v = [dpv[i][2] for i in range(offset-buff, offset+1)]
  sp = p[:-1:step]
  sv = v[:-1:step]
  assert len(sp) == num - 1
  assert len(sv) == num - 1
  ap = [sum(p[i:])/len(p[i:]) for i in range(0, len(p)-1, step)]
  av = [sum(v[i:])/len(v[i:]) for i in range(0, len(v)-1, step)]
  assert len(ap) == num - 1
  assert len(av) == num - 1
  p1 = [(p[-1]-s)/(s+PRICE_BONUS) for s in sp]
  v1 = [(v[-1]-s)/(s+VOLUME_BONUS) for s in sv]
  p2 = [(p[-1]-a)/(a+PRICE_BONUS) for a in ap]
  v2 = [(v[-1]-a)/(a+VOLUME_BONUS) for a in av]
  return p1 + v1 + p2 + v2

def test(dpv, step, num):
  dpv = [[x[0], float(x[1]), float(x[2])] for x in dpv]
  buff = step*(num-1)
  print 'Testing %s with step %d and num %d' % (dpv, step, num)
  for i in range(buff, len(dpv)):
    print 'offset: %d, features: %s' % (i, compute_features(dpv, i, step, num))

def main():
  if TEST:
    print 'Testing ... will exit after done'
    test([['d', 1, 2], ['d', 2, 3], ['d', 3, 4]], 1, 1)
    test([['d', 1, 2], ['d', 2, 3], ['d', 3, 4]], 1, 2)
    test([['d', 1, 2],
          ['d', 2, 3],
          ['d', 3, 4],
          ['d', 4, 5],
          ['d', 5, 6],
          ['d', 6, 7],
          ['d', 7, 8],
          ['d', 8, 9]],
          2, 4)
    return

  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--data_dir', required=True)
  parser.add_argument('--step', required=True)
  parser.add_argument('--num', required=True)
  parser.add_argument('--min_date', required=True)
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  step = int(args.step)
  num = int(args.num)
  assert step > 0
  assert num > 0
  buff = step*(num-1)
  output_dir = args.output_dir.rstrip('/')
  output_folder = output_dir[output_dir.rfind('/')+1:]
  _, s, n = output_folder.split('_')
  assert step == int(s)
  assert num == int(n)

  processed_dates, skipped_dates = 0, 0
  for i in range(len(tickers)):
    ticker = tickers[i]
    print 'Processing %d/%d: %s' % (i+1, len(tickers), ticker)
    input_file = '%s/%s.txt' % (args.data_dir, ticker)
    if not os.path.isfile(input_file):
      print('!! %s does not exist, skipping' % input_file)
      continue
    with open(input_file, 'r') as fp:
      lines = fp.read().splitlines()
    dpv = []
    for line in lines:
      d, p, v = line.split(' ')
      dpv.append([d, float(p), float(v)])
    output = []
    skipped_dates += buff
    for j in range(buff, len(dpv)):
      if dpv[j][0] < args.min_date:
        skipped_dates += 1
        continue
      processed_dates += 1
      features = compute_features(dpv, j, step, num)
      assert len(features) == (num-1)*4
      output.append([dpv[j][0]] + features)
    output_file = '%s/%s.pkl' % (args.output_dir, ticker)
    fp = open(output_file, 'wb')
    pickle.dump(output, fp, 1)
    fp.close()
  print 'processed %d data points, skipped %d' % (
      processed_dates, skipped_dates)

if __name__ == '__main__':
  main()

