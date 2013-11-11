#!/usr/bin/python

import pickle

bonus = 0.01
max_gain = 10.0  # Cap on max gain to avoid data errors.
price_map_file = './price_map.pkl'
# Price map may contain more than open dates for certain stocks, so we still
# need this to filter those out.
date_file = './open_dates_sanitized.txt'
step = 5  # Compute gains every 'step' open dates.
lookahead = 10  # Look ahead 'lookahead' days for computing gains.
# Percentages of sorted stocks for which gains are averaged and outputted.
percs = [
    ['t1', 0.01],
    ['t10', 0.1],
    ['t25', 0.25],
    ['mid', 0.5],
    ['b25', -0.25],
    ['b10', -0.1],
    ['b1', -0.01],
    ['mkt', 1.0],
]

output_file = 'tmp/gain_distribution_%d_%d.csv' % (step, lookahead)

print 'Reading price map...'
fp = open(price_map_file, 'rb')
price_map = pickle.load(fp)
fp.close()

price_dates = set(price_map.keys())
min_date = min(price_dates)
with open(date_file, 'r') as fp:
  open_dates = set([d for d in fp.read().splitlines() if d >= min_date])
assert open_dates <= price_dates
dates = sorted(open_dates)

dead = set()
with open(output_file, 'w') as fp:
  headers = ['date'] + [p[0] for p in percs]
  print >> fp, ','.join(headers)
  avg_output = None
  count = 0
  for i in range(0, len(dates)-lookahead, step):
    print 'Processing %s' % dates[i]
    pm1 = price_map[dates[i]]
    pm2 = price_map[dates[i+lookahead]]
    # Sanity check.  May not work if min_date is before 1995-01-03.
    assert len(pm1) >= 1000
    assert len(pm2) >= 1000
    gains = []
    for k, p1 in pm1.items():
      p2 = pm2.get(k)
      if p2 is None:
        dead.add(k)
        p2 = 0.0
      gain = (p2-p1)/(p1+bonus)
      gain = min(max_gain, gain)
      gains.append(gain)
    gains.sort(reverse=True)
    n = len(gains)
    output = []
    for p in percs:
      m = int(n*p[1])
      assert m != 0 and abs(m) <= n
      if m > 0:
        section = gains[:m]
      else:
        section = gains[m:]
      assert len(section) == abs(m)
      output.append(sum(section)/len(section))
    assert len(output) == len(percs)
    print >> fp, ','.join([dates[i]] + ['%.4f%%' % (o*100) for o in output])
    if avg_output is None:
      avg_output = output
    else:
      assert len(avg_output) == len(output)
      for j in range(len(output)):
        avg_output[j] += output[j]
    count += 1
  assert avg_output is not None and count > 0
  assert len(avg_output) == len(percs)
  for j in range(len(avg_output)):
    avg_output[j] /= count
  print >> fp, ','.join(['avg'] + ['%.4f%%' % (o*100) for o in avg_output])
  
print '%d dead stocks: %s' % (len(dead), dead)

