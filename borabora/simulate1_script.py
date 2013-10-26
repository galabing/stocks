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
ticker_filter_file='%s/tickers.txt' % data_dir

tmp_output_file = './simulate1.tmpout'
gain_file = './simulate1.gain.csv'
sharpe_file = './simulate1.sharpe.csv'

ks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 45, 50]
hs = [7*i for i in range(1, 14)]

#ks = [1, 2]
#hs = [7*i for i in range(1, 3)]

def write_csv(output_file, output_map, index):
  with open(output_file, 'w') as fp:
    print('h/k,%s' % (','.join([str(k) for k in ks])), file=fp)
    for h in hs:
      print('%d,%s' % (h, ','.join([output_map['%d-%d' % (k, h)][index] for k in ks])), file=fp)

output_map = dict()
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

