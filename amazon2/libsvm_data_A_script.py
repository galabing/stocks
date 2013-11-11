#!/usr/bin/python

run_training = False  # collect training data or testing data

symbol = 'A'
training_metadata_dir = './training_metadata_%s' % symbol
testing_metadata_dir = './testing_metadata_%s' % symbol
training_data_dir = './training_data/%s' % symbol
testing_data_dir = './testing_data/%s' % symbol
logs_dir = './logs'
data_map = {
  'onew': ['features_1_66', 'meta_5'],
  'twow': ['features_2_66', 'meta_10'],
  'onem': ['features_5_53', 'meta_20'],
  'oneq': ['features3_10_53', 'meta_65'],
  'twoq': ['features_20_53', 'meta_130'],
  'oney': ['features_20_53', 'meta_260'],
}

for k, v in data_map.items():
  f, m = v
  if run_training:
    log_file = '%s/training_data_%s_%s.log' % (logs_dir, symbol, k)
    cmd = ('nohup ./collect_libsvm_data.py --metadata_file=%s/%s.txt'
           ' --feature_dir=./%s --max_pos_count=20000 --max_neg_count=20000'
           ' --output_dir=%s/%s > %s &' % (
               training_metadata_dir, m, f, training_data_dir, k, log_file))
  else:
    log_file = '%s/testing_data_%s_%s.log' % (logs_dir, symbol, k)
    cmd = ('nohup ./collect_libsvm_data.py --metadata_file=%s/%s.txt'
           ' --feature_dir=./%s --max_pos_count=-1 --max_neg_count=-1'
           ' --output_dir=%s/%s > %s &' % (
               testing_metadata_dir, m, f, testing_data_dir, k, log_file))
  print cmd

