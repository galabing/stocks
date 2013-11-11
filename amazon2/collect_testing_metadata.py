#!/usr/bin/python

""" Collects testing metadata:

    Given a cutoff date D, lookahead period L, sampling step S, sampling period
    number P, collects the following metadata for training:
    - for every S days after cutoff date D, up to period P, calculate
      and sort gains for all stocks on that date
    - classify gains into {+1, -1} classes
    - output <date> <ticker> <label> <gain> <perc>

    Set P to -1 to collect all available dates after cutoff.

    Classification of gains into {+1, -1} is controlled by flags
    --max_pos_rank, --min_neg_rank or --min_pos_gain, --max_neg_gain.
    One and only one set of flags must be set.

    Eg, setting max_pos_rank to 0.25 and min_neg_rank to 0.75 will result in
    the top 25% gains being assigned +1, bottom 25% -1 and the 50% in between
    dropped.

    Eg, setting min_pos_gain to 0.1 and max_neg_gain to -0.1 will result in
    stocks with 10+% gains being assigned +1, with 10+% losses being assgined
    -1 and the ones in between dropped.
"""

import argparse
import pickle

BONUS = 0.01
MAX_GAIN = 10.0

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--date_file', required=True)
  parser.add_argument('--price_map_file', required=True)
  parser.add_argument('--cutoff_date', required=True)
  parser.add_argument('--lookahead', required=True)
  parser.add_argument('--sample_step', required=True)
  parser.add_argument('--sample_period', required=True)
  parser.add_argument('--max_pos_rank')
  parser.add_argument('--min_neg_rank')
  parser.add_argument('--min_pos_gain')
  parser.add_argument('--max_neg_gain')
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()

  lookahead = int(args.lookahead)
  step = int(args.sample_step)
  period = int(args.sample_period)
  assert lookahead > 0
  assert step > 0

  max_pos_rank, min_neg_rank = None, None
  if args.max_pos_rank is not None and args.min_neg_rank is not None:
    max_pos_rank = float(args.max_pos_rank)
    min_neg_rank = float(args.min_neg_rank)
    assert max_pos_rank > 0 and max_pos_rank < 1
    assert min_neg_rank > 0 and min_neg_rank < 1
    assert max_pos_rank <= min_neg_rank
  min_pos_gain, max_neg_gain = None, None
  if args.min_pos_gain is not None and args.max_neg_gain is not None:
    min_pos_gain = float(args.min_pos_gain)
    max_neg_gain = float(args.max_neg_gain)
    assert min_pos_gain >= max_neg_gain
  # Each set of flags must be set together, but the two sets are mutually
  # exclusive.
  assert (max_pos_rank is None) == (min_neg_rank is None)
  assert (min_pos_gain is None) == (max_neg_gain is None)
  assert (max_pos_rank is None) != (min_pos_gain is None)
  use_rank = max_pos_rank is not None

  print 'Loading price map...'
  fp = open(args.price_map_file, 'rb')
  price_map = pickle.load(fp)
  fp.close()
  print 'Loaded price map with %d entries' % len(price_map)

  min_date = min(price_map.keys())
  with open(args.date_file, 'r') as fp:
    open_dates = set([d for d in fp.read().splitlines() if d >= min_date])
  assert open_dates <= set(price_map.keys())
  dates = sorted([d for d in open_dates if d > args.cutoff_date])
  max_date = dates[-1]
  print '%d open dates between cutoff date %s and max date %s' % (
      len(dates), args.cutoff_date, max_date)
  if period > 0 and period < len(dates):
    dates = dates[:period]
  print '%d open dates within sampling period %s ... %s' % (
      len(dates), dates[0], dates[-1])

  with open(args.output_file, 'w') as fp:
    print >> fp, 'cutoff=%s lookahead=%d step=%d period=%d' % (
        args.cutoff_date, lookahead, step, period)
    for i in range(0, len(dates)-lookahead, step):
      print 'Processing sample date: %s' % dates[i]
      pm1 = price_map[dates[i]]
      pm2 = price_map[dates[i+lookahead]]
      gains = []
      for k, p1 in pm1.items():
        p2 = pm2.get(k)
        if p2 is None:
          p2 = 0.0
        gain = (p2-p1)/(p1+BONUS)
        gain = min(MAX_GAIN, gain)
        gains.append([k, gain])
      gains.sort(key=lambda gain: gain[1], reverse=True)
      if use_rank:
        max_pos = int(len(gains)*max_pos_rank)
        min_neg = int(len(gains)*min_neg_rank)
      else:
        max_pos, min_neg = 0, len(gains)
        for j in range(len(gains)):
          if gains[j][1] > min_pos_gain:
            max_pos = j+1
          if gains[j][1] < max_neg_gain:
            min_neg = min(min_neg, j-1)
      print ('%d gains calculated, %d pos (max=%.4f%%, min=%.4f%%)'
             ', %d neg (min=%.4f%%, max=%.4f%%)' % (
             len(gains), max_pos, gains[0][1]*100, gains[max_pos-1][1]*100,
             len(gains)-min_neg-1, gains[-1][1]*100, gains[min_neg+1][1]*100))
      for j in range(max_pos):
        print >> fp, '%s %s +1 %.4f%% %.4f%%' % (
            dates[i], gains[j][0], gains[j][1]*100, j*100.0/len(gains))
      for j in range(min_neg+1, len(gains)):
        print >> fp, '%s %s -1 %.4f%% %.4f%%' % (
            dates[i], gains[j][0], gains[j][1]*100, j*100.0/len(gains))

if __name__ == '__main__':
  main()

