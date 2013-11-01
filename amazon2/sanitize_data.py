#!/usr/bin/python

""" Sanitizes historical stock data, extracts price and volume, skips files
    with unfillable holes (for now missing more than one consecutive open
    dates).
"""

import argparse
import os

def sanitize(dpv, open_dates):
  min_date = min(dpv.keys())
  max_date = max(dpv.keys())
  for i in range(len(open_dates)):
    date = open_dates[i]
    if date < min_date or date > max_date:
      continue
    if date in dpv: continue
    if i == 0 or i == len(open_dates) - 1:
      return False
    pd = open_dates[i-1]
    nd = open_dates[i+1]
    if pd not in dpv or nd not in dpv:
      return False
    p = (dpv[pd][0] + dpv[nd][0])/2
    v = (dpv[pd][1] + dpv[nd][1])/2
    dpv[date] = [p, v]
  return True

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--date_file', required=True)
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()

  with open(args.date_file, 'r') as fp:
    open_dates = fp.read().splitlines()

  ok_count = 0
  for i in range(len(tickers)):
    ticker = tickers[i]
    print 'Processing %d/%d: %s' % (i+1, len(tickers), ticker)
    input_file = '%s/%s.csv' % (args.input_dir, ticker)
    if not os.path.isfile(input_file):
      print '!! %s does not exist, skipping' % input_file
      continue
    with open(input_file, 'r') as fp:
      lines = fp.read().splitlines()
    assert len(lines) > 0
    assert lines[0] == 'Date,Open,High,Low,Close,Volume,Adj Close'
    dpv = dict()
    pd = None
    for line in lines[:0:-1]:
      d, o, h, l, c, v, a = line.split(',')
      if pd is not None:
        assert pd < d
      pd = d
      a, v = float(a), float(v)
      assert a >= 0 and v >= 0
      dpv[d] = [a, v]
    ok = sanitize(dpv, open_dates)
    if not ok: continue
    output_file = '%s/%s.txt' % (args.output_dir, ticker)
    with open(output_file, 'w') as fp:
      for d in sorted(dpv.keys()):
        p, v = dpv[d]
        print >> fp, '%s %.2f %.2f' % (d, p, v)
    ok_count += 1
  print '%d of %d files are sanitized' % (ok_count, len(tickers))

if __name__ == '__main__':
  main()

