#!/usr/local/bin/python3

""" Basic simulation:
    - after each ranking file published, buy top k stocks
    - hold for h days and sell
"""

import argparse
import datetime
import os
import utils

def get_trans(price_map, tickers, date, holding_period):
  trans = []
  for ticker in tickers:
    bdate, bprice = utils.get_price(price_map, ticker, date)
    if bdate is None or bprice is None:
      continue
    tdate = (datetime.datetime.strptime(bdate, '%Y-%m-%d') + holding_period).strftime('%Y-%m-%d')
    sdate, sprice = utils.get_price(price_map, ticker, tdate)
    if sdate is None or sprice is None:
      if utils.is_ticker_dead(price_map, ticker):
        utils.printd('!! %s dead' % ticker)
        sdate, sprice = tdate, 0
      else:
        continue
    trans.append([ticker, bdate, bprice, sdate, sprice])
  return trans

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--price_map_file', required=True)
  parser.add_argument('--ticker_filter_file')
  parser.add_argument('--ranking_dir', required=True)
  parser.add_argument('--k', required=True)
  parser.add_argument('--h', required=True)
  parser.add_argument('--real', action='store_true')
  parser.add_argument('--market_data_file')
  args = parser.parse_args()

  ticker_filter = set()
  if args.ticker_filter_file:
    with open(args.ticker_filter_file, 'r') as fp:
      ticker_filter = set(fp.read().splitlines())

  k = int(args.k)
  h = int(args.h)
  assert k != 0
  assert h > 0
  holding_period = datetime.timedelta(days=h)

  dates = sorted([f[:f.find('.')] for f in os.listdir(args.ranking_dir) if f.endswith('.csv')])
  utils.printd('simulating %d dates' % len(dates))

  utils.printd('loading price map...')
  price_map = utils.read_price_map(args.price_map_file)
  utils.printd('done, %d entries in the price map' % len(price_map))

  if len(ticker_filter) > 0:
    index = None
  elif k > 0:
    index = range(1, k+1)
  else:
    index = range(-1, k-1, -1)
  all_trans = []
  for date in dates:
    ranking_file = '%s/%s.csv' % (args.ranking_dir, date)
    if len(ticker_filter) > 0:
      tickers = utils.read_tickers_by_filter(ranking_file, k, ticker_filter)
    else:
      tickers = utils.read_tickers_by_index(ranking_file, index)
    trans = get_trans(price_map, tickers, date, holding_period)
    if len(trans) == 0:
      continue
    utils.printd('%s: %s' % (date, utils.get_string(trans, h, args.real)))
    all_trans.extend(trans)
  utils.printd(utils.get_string(all_trans, h, args.real))
  gains = utils.get_gains(all_trans, args.real)
  avg_gain = sum(gains)/len(gains)
  print(avg_gain/h*100)

  if args.market_data_file:
    mtrans = utils.simulate_market_trans(all_trans, args.market_data_file)
    utils.printd('market:')
    utils.printd(utils.get_string(mtrans, h, False))
    sharpe = utils.compute_sharpe_ratio(all_trans, mtrans, args.real)
    utils.printd('sharpe ratio: %.4f' % sharpe)
    print(sharpe)

if __name__ == '__main__':
  main()

