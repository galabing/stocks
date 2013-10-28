#!/usr/local/bin/python3
#
# eg:
#   ./simulate2.py --price_map_file=../../data_stocks/borabora/price_map.txt --ranking_dir=../../data_stocks/borabora/rankings --ticker_file=../../data_stocks/borabora/secind/Technology/tickers.txt --k=1 --h=28 --real

import os

# modify as needed
data_dir = '../../data_stocks/borabora'
price_map_file = '%s/price_map.txt' % data_dir
ranking_dir = '%s/rankings' % data_dir

tmp_output_file = './simulate1.tmpout'
base_output_dir = '%s/simulate2_clusters' % data_dir

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

ks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
hs = [7*i for i in range(1, 14)]

def write_csv(output_file, output_map):
  with open(output_file, 'w') as fp:
    print('diff h/k,%s' % (','.join([str(k) for k in ks])), file=fp)
    for h in hs:
      print('%d,%s' % (h, ','.join(['%.2f%%' % (output_map['%d-%d' % (k, h)][0] - output_map['%d-%d' % (k,h)][1]) for k in ks])), file=fp)
    print('rank h/k,%s' % (','.join([str(k) for k in ks])), file=fp)
    for h in hs:
      print('%d,%s' % (h, ','.join(['%.2f%%' % output_map['%d-%d' % (k, h)][0] for k in ks])), file=fp)
    print('market h/k,%s' % (','.join([str(k) for k in ks])), file=fp)
    for h in hs:
      print('%d,%s' % (h, ','.join(['%.2f%%' % output_map['%d-%d' % (k, h)][1] for k in ks])), file=fp)

output_map = dict()
for tff in tffs:
  ticker_file = '%s/%s' % (data_dir, tff)
  output_dir = '%s/%s' % (base_output_dir, tff[:tff.rfind('/')].replace('/', '__'))
  if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
  output_file = '%s/gain.csv' % output_dir
  if os.path.isfile(output_file):
    print('%s was done' % output_file)
    continue
  for k in ks:
    for h in hs:
      cmd = './simulate2.py --price_map_file=%s --ranking_dir=%s --ticker_file=%s --k=%d --h=%d --real > %s' % (price_map_file, ranking_dir, ticker_file, k, h, tmp_output_file)
      print(cmd)
      assert os.system(cmd) == 0
      with open(tmp_output_file, 'r') as fp:
        lines = fp.read().splitlines()
      assert len(lines) == 2
      output_map['%d-%d' % (k, h)] = [float(lines[0]), float(lines[1])]
  write_csv(output_file, output_map)

