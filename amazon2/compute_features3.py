#!/usr/bin/python

import argparse
import math
import os
import pickle

PRICE_BONUS = 0.01
VOLUME_BONUS = 1.0
EPS = 1e-5

TEST = False

def compute_derivatives(v, bonus):
  return [(v[i+1]-v[i])/(v[i]+bonus) for i in range(len(v)-1)]

def normalize(v):
  if len(v) == 0:
    return [], 1
  m = sum(v)/len(v)
  n = [x - m for x in v]
  l = math.sqrt(sum([x*x for x in n]))
  if l >= EPS:
    ok = 1
  else:
    ok = 0
  if ok > 0:
    n = [x/l for x in n]
  return n, ok

def compute_features(dpv, offset, step, num):
  buff = step*(num-1)
  assert offset >= buff
  p = [dpv[i][1] for i in range(offset-buff, offset+1, step)]
  v = [dpv[i][2] for i in range(offset-buff, offset+1, step)]
  assert len(p) == num
  assert len(v) == num
  dp = compute_derivatives(p, PRICE_BONUS)
  dv = compute_derivatives(v, VOLUME_BONUS)
  assert len(dp) == num - 1
  assert len(dv) == num - 1
  np, pok = normalize(p)
  ndp, dpok = normalize(dp)
  ndv, dvok = normalize(dv)
  return np + ndp + ndv, 3 - pok - dpok - dvok

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

  all_noks = [0, 0]
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
      features, noks = compute_features(dpv, j, step, num)
      assert len(features) == num + (num-1)*2
      assert noks >= 0
      assert noks <= 3
      all_noks[0] += noks
      all_noks[1] += 3
      output.append([dpv[j][0]] + features)
    output_file = '%s/%s.pkl' % (args.output_dir, ticker)
    fp = open(output_file, 'wb')
    pickle.dump(output, fp, 1)
    fp.close()
  print 'processed %d data points, skipped %d' % (
      processed_dates, skipped_dates)
  print '%d (out of %d) normalization errors' % (all_noks[0], all_noks[1])

if __name__ == '__main__':
  main()

