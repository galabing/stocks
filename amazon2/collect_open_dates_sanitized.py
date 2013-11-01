#!/usr/bin/python

""" Collects open dates from historical data.
"""

import argparse
import datetime
import os

# Define a date to be open if 90% of the stocks overlapping this date are open.
# This yields an approx 69% of open dates, which aligns with reality considering
# stocks trade Monday through Friday except for 9 public holidays.
MIN_RATIO = 0.9

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--data_dir', required=True)
  parser.add_argument('--output_file', required=True)
  parser.add_argument('--debug_file')
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()

  date_map = dict()
  for i in range(len(tickers)):
    ticker = tickers[i]
    print 'Processing %d/%d: %s' % (i+1, len(tickers), ticker)
    input_file = '%s/%s.txt' % (args.data_dir, ticker)
    if not os.path.isfile(input_file):
      print '!! %s does not exist, skipping' % input_file
      continue
    with open(input_file, 'r') as fp:
      lines = fp.read().splitlines()
    # Update market dates for this stock (numerator).
    pd = None
    for line in lines:
      d, p, v = line.split(' ')
      if pd is not None:
        assert d > pd
      pd = d
      if d not in date_map:
        date_map[d] = [1, 0]
      else:
        date_map[d][0] += 1
    # Update all dates for this stock (denominator).
    fd = lines[0][:lines[0].find(' ')]
    ld = lines[-1][:lines[-1].find(' ')]
    assert fd < ld
    date = datetime.datetime.strptime(fd, '%Y-%m-%d')
    delta = datetime.timedelta(days=1)
    while True:
      d = date.strftime('%Y-%m-%d')
      if d not in date_map:
        date_map[d] = [0, 1]
      else:
        date_map[d][1] += 1
      if d >= ld:
        break
      date += delta

  ratio_map = dict()
  max_below, min_above = [None, 0.0], [None, 1.0]
  for k, v in date_map.items():
    assert v[0] >= 0
    assert v[1] > 0
    assert v[0] <= v[1]
    ratio = float(v[0])/v[1]
    if ratio >= MIN_RATIO:
      ratio_map[k] = ratio
      if ratio < min_above[1]:
        min_above = [k, ratio]
    elif ratio > max_below[1]:
      max_below = [k, ratio]
  print '%d out of %d dates are open' % (len(ratio_map), len(date_map))
  print 'max below threshold: %s: %f' % (max_below[0], max_below[1])
  print 'min above threshold: %s: %f' % (min_above[0], min_above[1])

  with open(args.output_file, 'w') as fp:
    for k in sorted(ratio_map.keys()):
      print >> fp, k

  if args.debug_file:
    with open(args.debug_file, 'w') as fp:
      for k in sorted(ratio_map.keys()):
        print >> fp, '%s %d %d %f' % (
            k, date_map[k][0], date_map[k][1], ratio_map[k])

if __name__ == '__main__':
  main()

