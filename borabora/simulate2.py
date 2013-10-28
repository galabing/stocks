#!/usr/local/bin/python3

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
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--ranking_dir', required=True)
  parser.add_argument('--k', required=True)
  parser.add_argument('--h', required=True)
  parser.add_argument('--real', action='store_true')
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    ticker_filter = set(fp.read().splitlines())
  utils.printd('simulating %d tickers' % len(ticker_filter))

  k = int(args.k)
  h = int(args.h)
  assert h > 0
  holding_period = datetime.timedelta(days=h)

  dates = sorted([f[:f.find('.')] for f in os.listdir(args.ranking_dir) if f.endswith('.csv')])
  utils.printd('simulating %d dates' % len(dates))

  utils.printd('loading price map...')
  price_map = utils.read_price_map(args.price_map_file)
  utils.printd('done, %d entries in the price map' % len(price_map))

  all_trans, all_mtrans = [], []
  for date in dates:
    ranking_file = '%s/%s.csv' % (args.ranking_dir, date)
    tickers = utils.read_tickers_by_filter(ranking_file, k, ticker_filter)
    trans = get_trans(price_map, tickers, date, holding_period)
    if len(trans) == 0:
      utils.printd('no trans for %s' % date)
      continue
    mtickers = utils.read_tickers_by_filter(ranking_file, 0, ticker_filter)
    mtrans = get_trans(price_map, mtickers, date, holding_period)
    utils.printd('%s (ranking): %s' % (date, utils.get_string(trans, h, args.real)))
    utils.printd('%s (market): %s' % (date, utils.get_string(mtrans, h, args.real)))
    all_trans.extend(trans)
    all_mtrans.extend(mtrans)
  utils.printd('all (ranking): %s' % utils.get_string(all_trans, h, args.real))
  utils.printd('all (market): %s' % utils.get_string(all_mtrans, h, args.real))
  gains = utils.get_gains(all_trans, args.real)
  avg_gain = sum(gains)/len(gains)
  print(avg_gain/h*100)
  mgains = utils.get_gains(all_mtrans, args.real)
  avg_mgain = sum(mgains)/len(mgains)
  print(avg_mgain/h*100)

if __name__ == '__main__':
  main()

