#!/usr/bin/python

""" Note: this script only works if testing is done on a weekly basis.
"""

import argparse
import pickle

CASH = 10000.0

def get_fees(shares, opt):
  global oh_wins, ib_wins
  if opt == '':
    return 0.0
  if opt == 'oh':
    return 3.95
  assert opt == 'ib'
  f = 0.005*shares
  return max(1.0, f)

def get_balance(cash, stock_map):
  balance = cash
  for ticker, shares_price in stock_map.items():
    shares, price = shares_price
    balance += shares*price
  return balance

def get_stats_string(label, v):
  return ('%s: 1%%=%.2f 10%%=%.2f 25%%=%.2f 50%%=%.2f 75%%=%.2f'
           ' 90%%=%.2f 99%%=%.2f avg=%.2f' % (
             label,
             v[int(0.01*len(v))],
             v[int(0.10*len(v))],
             v[int(0.25*len(v))],
             v[int(0.50*len(v))],
             v[int(0.75*len(v))],
             v[int(0.90*len(v))],
             v[int(0.99*len(v))],
             sum(v)/len(v)))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--libsvm_output_file', required=True)
  parser.add_argument('--libsvm_meta_file', required=True)
  parser.add_argument('--open_date_file', required=True)
  parser.add_argument('--price_map_file', required=True)
  parser.add_argument('--lookahead_weeks', required=True)
  parser.add_argument('--simulation_weeks', default='52')
  # Number or ratio of top-ranked stocks to trade.  Must specify one.
  parser.add_argument('--num')
  parser.add_argument('--ratio')
  # 'oh' for optionshouse or 'ib' for interactive broker or '' for no fee.
  parser.add_argument('--fee_option', required=True)
  # By default it will try all starting points.  If this is specified it will
  # only try one starting point (the first date in the metadata).
  parser.add_argument('--try_one', action='store_true')
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()

  lookahead = int(args.lookahead_weeks)
  assert lookahead > 0
  period = int(args.simulation_weeks)
  assert period >= lookahead

  num, ratio = None, None
  if args.num:
    num = int(args.num)
    assert num > 0
  if args.ratio:
    ratio = float(args.ratio)
    assert ratio > 0 and ratio < 1
  assert (num is None) != (ratio is None)

  fee_option = args.fee_option
  assert fee_option == '' or fee_option == 'oh' or fee_option == 'ib'

  print 'loading open dates...'
  with open(args.open_date_file, 'r') as fp:
    open_dates = fp.read().splitlines()
  print '%d open dates' % len(open_dates)

  print 'loading libsvm metadata...'
  with open(args.libsvm_meta_file, 'r') as fp:
    meta_lines = fp.read().splitlines()
  ticker_map = dict()
  for line in meta_lines:
    ticker, date = line.split(' ')
    if date not in ticker_map:
      ticker_map[date] = [ticker]
    else:
      ticker_map[date].append(ticker)

  print 'loading libsvm output...'
  with open(args.libsvm_output_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(lines) == len(meta_lines) + 1
  assert lines[0] == 'labels 1 -1'
  prob_map = dict()
  for i in range(1, len(lines)):
    label, pos, neg = lines[i].split(' ')
    label, pos, neg = int(label), float(pos), float(neg)
    assert label == 1 or label == -1
    assert abs(pos + neg - 1) < 1e-5
    ticker, date = meta_lines[i-1].split(' ')
    if date not in prob_map:
      prob_map[date] = [[ticker, pos]]
    else:
      prob_map[date].append([ticker, pos])
  for probs in prob_map.values():
    probs.sort(key=lambda prob: prob[1], reverse=True)
  print '%d dates with %d predictions' % (len(prob_map), len(meta_lines))

  print 'loading price map...'
  with open(args.price_map_file, 'rb') as fp:
    price_map = pickle.load(fp)
  print '%d entries in price map' % len(price_map)

  dates = sorted(prob_map.keys())
  if args.try_one:
    s = 1
  else:
    s = len(dates)
  print 'running simulation for %d dates' % s

  output = []
  for i in range(s):
    #print 'simulating from %s' % dates[i]
    cash = CASH
    stock_map = dict()  # ticker => [shares, price_per_share]
    total_fees = 0.0
    enough_data = True
    for j in range(0, period, lookahead):
      if i+j >= len(dates):
        print 'not enough data for %s' % dates[i]
        enough_data = False
        break
      date = dates[i+j]
      pm = price_map[date]
      #print '== %s - cash: %f, stocks: %s, balance: %f' % (
      #    date, cash, stock_map.keys(), get_balance(cash, stock_map))
      probs = prob_map[date]
      if num is not None:
        n = min(num, len(probs))
      else:
        n = int(len(probs)*ratio)
      picks = set([probs[k][0] for k in range(n)])
      sells = [ticker for ticker in stock_map.keys() if ticker not in picks]
      buys = [ticker for ticker in picks if ticker not in stock_map]
      #print '==== sells: %s' % sells
      #print '==== buys: %s' % buys
      for ticker in sells:
        shares = stock_map[ticker][0]
        if ticker in pm:
          sell_price = pm[ticker]
        else:
          sell_price = 0.0
        fees = get_fees(shares, fee_option)
        cash += shares*sell_price - fees
        total_fees += fees
        del stock_map[ticker]
      if len(buys) == 0:
        continue
      cash_per_stock = cash / len(buys)
      actual_buys = []
      for ticker in buys:
        buy_price = pm[ticker]
        if cash_per_stock >= buy_price:
          actual_buys.append(ticker)
      if len(actual_buys) == 0:
        continue
      cash_per_stock = cash / len(actual_buys)
      for ticker in actual_buys:
        buy_price = pm[ticker]
        shares = int(cash_per_stock/buy_price)
        assert shares > 0
        fees = get_fees(shares, fee_option)
        cash -= shares*buy_price + fees
        total_fees += fees
        stock_map[ticker] = [shares, buy_price]
    if not enough_data:
      break
    output.append([dates[i], CASH, get_balance(cash, stock_map), total_fees])

  balancev = sorted([o[2] for o in output], reverse=True)
  gainv = sorted([(o[2]-o[1])*100/o[1] for o in output], reverse=True)
  feesv = sorted([o[3] for o in output], reverse=True)
  print 'simulated %d cycles' % len(output)
  print get_stats_string('end_balances', balancev)
  print get_stats_string('gains', gainv)
  print get_stats_string('fees', feesv)

  with open(args.output_file, 'w') as fp:
    print >> fp, 'date,balance0,balance1,gain,fees'
    for o in output:
      date, balance0, balance1, fees = o
      print >> fp, '%s,%.2f,%.2f,%.2f%%,%.2f' % (
          date, balance0, balance1, (balance1-balance0)*100/balance0, fees)

if __name__ == '__main__':
  main()

