#!/usr/local/bin/python3
#
# eg:
#   ./simulate1.py --price_map_file=../../data_stocks/borabora/price_map.txt --ranking_dir=../../data_stocks/borabora/rankings/ --market_data_file=../../data_stocks/borabora/russell3000/_RUA.csv --real --k=10 --h=28 --ticker_filter_file=../../data_stocks/borabora/tickers.txt

import os

# modify as needed
data_dir = '../../data_stocks/borabora'
price_map_file = '%s/price_map.txt' % data_dir
ranking_dir = '%s/rankings' % data_dir
market_data_file = '%s/russell3000/_RUA.csv' % data_dir

tmp_output_file = './simulate1.tmpout'
#base_output_dir = '%s/simulate1_clusters' % data_dir
#base_output_dir = '%s/simulate1_experiments/cg_hc_ig_s_t.mic_sma_mid.0_5_10_25_100' % data_dir
base_output_dir = '%s/simulate1_clusters/allinfilter' % data_dir

tffs = [
    'cap/micro/tickers.txt',
    'cap/small/tickers.txt',
    'cap/mid/tickers.txt',
    'cap/large/tickers.txt',
    'price/0-5/tickers.txt',
    'price/5-10/tickers.txt',
    'price/10-15/tickers.txt',
    'price/15-20/tickers.txt',
    'price/20-25/tickers.txt',
    'price/25-30/tickers.txt',
    'price/30-40/tickers.txt',
    'price/40-50/tickers.txt',
    'price/50-75/tickers.txt',
    'price/75-100/tickers.txt',
    'price/100-inf/tickers.txt',
    'secind/Basic_Materials/tickers.txt',
    'secind/Consumer_Goods/tickers.txt',
    'secind/Financial/tickers.txt',
    'secind/Healthcare/tickers.txt',
    'secind/Industrial_Goods/tickers.txt',
    'secind/Services/tickers.txt',
    'secind/Technology/tickers.txt',
    'secind/Utilities/tickers.txt',
]
tffs = [
#    'simulate1_experiments/tech_micro_5-10/tickers.txt',
#    'simulate1_experiments/cg_hc_ig_s_t.mic_sma_mid.0_5_10_25_100/tickers.txt',
    'cap/micro/tickers.txt',
    'price/5-10/tickers.txt',
    'secind/Technology/tickers.txt',
]
#ks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 45, 50]
#ks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
ks = [0]
hs = [7*i for i in range(1, 14)]

def write_csv(output_file, output_map, index):
  with open(output_file, 'w') as fp:
    print('h/k,%s' % (','.join([str(k) for k in ks])), file=fp)
    for h in hs:
      print('%d,%s' % (h, ','.join([output_map['%d-%d' % (k, h)][index] for k in ks])), file=fp)

output_map = dict()
for tff in tffs:
  ticker_filter_file = '%s/%s' % (data_dir, tff)
  output_dir = '%s/%s' % (base_output_dir, tff[:tff.rfind('/')].replace('/', '__'))
  if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
  gain_file = '%s/gain.csv' % output_dir
  sharpe_file = '%s/sharpe.csv' % output_dir
  if os.path.isfile(gain_file) and os.path.isfile(sharpe_file):
    print('%s was done' % output_dir)
    continue
  for k in ks:
    for h in hs:
      cmd = './simulate1.py --price_map_file=%s --ranking_dir=%s --market_data_file=%s --real --k=%d --h=%d --ticker_filter_file=%s > %s' % (price_map_file, ranking_dir, market_data_file, k, h, ticker_filter_file, tmp_output_file)
      print(cmd)
      assert os.system(cmd) == 0
      with open(tmp_output_file, 'r') as fp:
        lines = fp.read().splitlines()
      assert len(lines) == 2
      gain = float(lines[0])
      sharpe = float(lines[1])
      output_map['%d-%d' % (k, h)] = ['%.4f%%' % gain, '%.4f' % sharpe]
  write_csv(gain_file, output_map, 0)
  write_csv(sharpe_file, output_map, 1)

