#!/usr/local/bin/python3

data_dir = '../../data_stocks/borabora/simulate1_experiments/cg_hc_ig_s_t.mic_sma_mid.0_5_10_25_100'
input_files = ['secind.txt', 'cap.txt', 'price.txt']
output_file = '%s/tickers.txt' % data_dir

tickers = None
for input_file in input_files:
  with open('%s/%s' % (data_dir, input_file), 'r') as fp:
    lines = set(fp.read().splitlines())
  print('%d tickers from %s' % (len(lines), input_file))
  if tickers is None:
    tickers = lines
  else:
    tickers &= lines
assert tickers is not None
print('%d tickers after join' % len(tickers))
with open(output_file, 'w') as fp:
  for t in sorted(tickers):
    print(t, file=fp)

