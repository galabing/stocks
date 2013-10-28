#!/usr/local/bin/python3

import datetime
import os
import utils

holding_period = 21
fund_per_stock = 625.0

data_dir = '../../data_stocks/borabora'
open_date_file = '%s/open_dates.txt' % data_dir
price_map_file = '%s/price_map.txt' % data_dir
ranking_dir = '%s/rankings' % data_dir

ticker_dir = data_dir
ticker_map = {
    'cap/micro/tickers.txt': 1,
    'price/0-5/tickers.txt': 1,
    'price/5-10/tickers.txt': 1,
    'secind/Technology/tickers.txt': 1,
}

def get_date(date, open_dates, max_delta=3):
  for d in open_dates:
    if d >= date:
      dd = datetime.datetime.strptime(d, '%Y-%m-%d')
      ddate = datetime.datetime.strptime(date, '%Y-%m-%d')
      assert (dd - ddate).days <= max_delta
      return d
  return None

def calculate_cost(stock_price, fund):
  n = int(fund/stock_price)
  f1 = n*0.005
  f2 = 1.0
  f = max(f1, f2)
  return n, stock_price*n, f*2  # ib
#  return n, stock_price*n, 3.95*2  # oh

# load ticker filters
ticker_filters = []
for k, v in ticker_map.items():
  ticker_file = '%s/%s' % (ticker_dir, k)
  print('loading ticker filter from %s' % ticker_file)
  with open(ticker_file, 'r') as fp:
    tickers = set(fp.read().splitlines())
  print('%d tickers loaded' % len(tickers))
  ticker_filters.append([tickers, v])
print('loaded %d ticker filters' % len(ticker_filters))

# load publication dates
dates = [rf[:rf.find('.')] for rf in os.listdir(ranking_dir) if rf.endswith('.csv')]
print('simulating at most %d dates: %s' % (len(dates), dates))

# read price map
price_map = utils.read_price_map(price_map_file)
print('loaded price map with %d entries' % len(price_map))

# read open dates
with open(open_date_file, 'r') as fp:
  open_dates = sorted(fp.read().splitlines())
print('loaded %d open dates, min: %s, max: %s' % (len(open_dates), open_dates[0], open_dates[-1]))

# start simulation
ticker_map = dict()
all_cost, all_return = 0.0, 0.0
count = 0
for date in sorted(dates):
  print('simulating %s' % date)
  bdate = get_date(date, open_dates)
  assert bdate is not None
  tdate = (datetime.datetime.strptime(bdate, '%Y-%m-%d') + datetime.timedelta(days=holding_period)).strftime('%Y-%m-%d')
  sdate = get_date(tdate, open_dates)
  if sdate is None:
    print('!! price is not available for target date: %s, skipping' % tdate)
    continue
  ranking_file = '%s/%s.csv' % (ranking_dir, date)
  tickers = []
  for ticker_filter in ticker_filters:
    ts = utils.read_tickers_by_filter(ranking_file, ticker_filter[1], ticker_filter[0])
    #ts = utils.read_tickers_by_filter_nodup(ranking_file, ticker_filter[1], ticker_filter[0], tickers)
    assert len(ts) == ticker_filter[1]
    tickers.extend(ts)
  #tickers = set(tickers)  # hack to avoid buying duplicates
  print('buying %d tickers: %s on %s, selling on %s' % (len(tickers), tickers, bdate, sdate))
  one_cost, one_return = 0.0, 0.0
  for ticker in tickers:
    pm = price_map[ticker]
    assert bdate in pm and sdate in pm
    bprice = pm[bdate]
    sprice = pm[sdate]
    n, cost, fees = calculate_cost(bprice, fund_per_stock)
    cost += fees
    ret = n*sprice - cost
    print('%s, buy = %.2f, sell = %.2f, shares = %d, fees = %.2f - cost = %.2f, return = %.2f (%.2f%%)' % (ticker, bprice, sprice, n, fees, cost, ret, ret*100/cost))
    one_cost += cost
    one_return += ret
  all_cost += one_cost
  all_return += one_return
  print('cost = %.2f, return = %.2f (%.2f%%)' % (one_cost, one_return, one_return*100/one_cost))
  for ticker in tickers:
    if ticker not in ticker_map:
      ticker_map[ticker] = 1
    else:
      ticker_map[ticker] += 1
  count += 1
print('bought %d tickers for %d dates:\n%s' % (len(ticker_map), count, sorted(ticker_map.items(), key=lambda item: item[1], reverse=True)))
print('all cost = %.2f, all return = %.2f (%.2f%%)' % (all_cost, all_return, all_return*100/all_cost))

