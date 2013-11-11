#!/usr/bin/python

import os

gain_map = {
#    5: 7.62/100,
    10: 11.08/100,
#    20: 16.37/100,
#    65: 33.88/100,
#    130: 55.20/100,
#    260: 94.13/100,
}

date_file = './open_dates_sanitized.txt'
price_map_file = './price_map.pkl'
cutoff_date = '2005-01-01'
sample_step = 5
sample_period = -1

training_dir = './training_metadata_A'
testing_dir = './testing_metadata_A'

def run(cmd):
  print cmd
  assert os.system(cmd) == 0

for g, t in gain_map.items():
  cmd = ('./collect_training_metadata.py --date_file=%s --price_map_file=%s'
         ' --cutoff_date=%s --lookahead=%d --sample_step=%d --sample_period=%d'
         ' --min_pos_gain=%f --max_neg_gain=%f'
         ' --output_file=%s/meta_%d.txt' % (
             date_file, price_map_file, cutoff_date, g, sample_step,
             sample_period, t, t, training_dir, g))
  run(cmd)
  cmd = ('./collect_testing_metadata.py --date_file=%s --price_map_file=%s'
         ' --cutoff_date=%s --lookahead=%d --sample_step=%d --sample_period=%d'
         ' --min_pos_gain=%f --max_neg_gain=%f'
         ' --output_file=%s/meta_%d.txt' % (
             date_file, price_map_file, cutoff_date, g, sample_step,
             sample_period, t, t, testing_dir, g))
  run(cmd)


