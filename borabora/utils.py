#!/usr/local/bin/python3

import csv
import datetime
import math
import os

debug = False

def printd(msg):
  if debug:
    print(msg)

# price data utils

def read_price_map_from_file(data_file, min_date='0000-00-00', max_date='9999-99-99'):
  with open(data_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(lines) > 0
  assert lines[0] == 'Date,Open,High,Low,Close,Volume,Adj Close'
  m = dict()
  pd = None
  for i in range(1, len(lines)):
    d, o, h, l, c, v, a = lines[i].split(',')
    if pd is not None:
      assert pd > d
    pd = d
    if d < min_date or d > max_date:
      continue
    m[d] = float(a)
  return m

def read_price_map_from_files(tickers, data_dir, min_date='0000-00-00', max_date='9999-99-99'):
  price_map = dict()
  for ticker in tickers:
    data_file = '%s/%s.csv' % (data_dir, ticker)
    if not os.path.isfile(data_file):
      continue
    m = read_price_map_from_file(data_file, min_date, max_date)
    if len(m) > 0:
      price_map[ticker] = m
  return price_map

def read_price_map(input_file):
  with open(input_file, 'r') as fp:
    lines = fp.read().splitlines()
  price_map = dict()
  for line in lines:
    ticker, items = line.split('=')
    assert items != ''
    items = items.split(',')
    m = dict()
    for item in items:
      d, p = item.split(':')
      m[d] = float(p)
    price_map[ticker] = m
  return price_map

def write_price_map(price_map, output_file):
  with open(output_file, 'w') as fp:
    for t, m in price_map.items():
      assert len(m) > 0
      data = ['%s:%f' % (d, p) for d, p in m.items()]
      print('%s=%s' % (t, ','.join(data)), file=fp)

def get_price_internal(m, date, max_delta=7):
  for d in range(max_delta+1):
    dd = (datetime.datetime.strptime(date, '%Y-%m-%d') + datetime.timedelta(days=d)).strftime('%Y-%m-%d')
    if dd in m:
      return dd, m[dd]
  return None, None

def get_price(price_map, ticker, date, max_delta=7):
  if ticker not in price_map:
    return None, None
  m = price_map[ticker]
  return get_price_internal(m, date, max_delta)

def is_ticker_dead(price_map, ticker):
  assert ticker in price_map
  ticker_max_date = max(price_map[ticker].keys())
  max_date = '0000-00-00'
  for ticker in price_map:
    max_date = max(max_date, max(price_map[ticker].keys()))
  return (datetime.datetime.strptime(max_date, '%Y-%m-%d') - datetime.datetime.strptime(ticker_max_date, '%Y-%m-%d')).days > 7

# ranking data utils

def read_tickers(ranking_file):
  with open(ranking_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(lines) >= 2
  assert lines[1] == "Ranking,Ticker,Name,# NA's,Final Stmt,100% Stock Rank,Value,Pr2CashFlTTM,Pr2FrCashFlTTM,Pr2SalesTTM,Pr2TanBkQ,PrSalesQ (intu),Earn Yield (intu),PEExclXorTTM (intu),PEG (intu),PEGLT (intu),PERelative (intu),P2BookQ (intu),ev,ev /fcf,ev / projected earnings,CurrYEPSEstvs4W,NextYEPSEstvs4W,EPS Chg TTM,EV/FCFTTM,EV/EBITDA TTM,PEG (intu)2,PE Excl (Intu),PR2FcashFlttm(intu),EV/EBITDATTM (intu),EV/SalesTTM (intu),BV / Price (intu),Prc2SalesIncDebt,FCFTTM/MktCap,FCFQ/MktCap,ROE%Q,ROE%Q3,Technical,Pr52WRel%Chg,Pr4WRel%Chg,Pr26WRel%Chg,sar,macd,Beta (intu),Price (intu),vma(150)/vma(300),ema(50)/ema(100),1movs6movol,close(0)/sma(10),3MoPctRet,3MoRet3MoAgo,3MoPctRet (intu),VolM% Shsout (intu),RSI(5),dummy,Profitability,EBITDMgn%5YAvg,ROA%TTM,ROI%5YAvg,40% ROA/ROE,ROA Change,ROE Change,ROE%TTM (intu),Liquidity,Inst%Own,Liquidity2,MktCap (intu),MktCap,AvgDailyTot(200),Absolute price,Investor Concerns,Buyback,Buyback4,FCFQ/AstTotQ,FCFQ / DbtTotQ,SIRatio,AnalystSentChg,AnalystEPSChg,Surprise%Q (intu),LT Grwth Rate (intu),3 Mo SI Decrease (intu),Recommendation | SI Interaction,SI % Float (intu),TATA,TACC_TTM,Short Interest,Downgrade4WkAgo,Downgrade8WkAgo,CurFY4Wk,CurFY8Wk,CurFY13Wk,NextFY4Wk,NextFY8Wk,NextFY13Wk,NextFYEPSRevisedSmall?4,NextFYEPSRevisedMid?4,NextFYEPSRevisedBig?4,NextFYEPSRevisedSmall?8,NextFYEPSRevisedMid?8,NextFYEPSRevisedBig?8"
  tickers = []
  for row in csv.reader(lines[2:], delimiter=','):
    if row[1] != '':
      tickers.append(row[1])
  return tickers

def read_tickers_by_filter(ranking_file, k, ticker_filter):
  all_tickers = read_tickers(ranking_file)
  if k < 0:
    all_tickers.reverse()
    k = -k
  tickers = []
  for t in all_tickers:
    if t not in ticker_filter:
      continue
    tickers.append(t)
    if len(tickers) >= k:
      break
  assert len(tickers) == k
  return tickers

def read_tickers_by_index(ranking_file, index=None):
  all_tickers = read_tickers(ranking_file)
  tickers = []
  if index is None:
    index = range(1, len(tickers)+1)
  for i in index:
    j = i
    if j < 0:
      j += len(all_tickers) + 1
    tickers.append(all_tickers[j-1])
  return tickers

# transaction utils

def simulate_market_trans(trans, market_data_file):
  m = read_price_map_from_file(market_data_file)
  max_date = max(m.keys())
  market = market_data_file[market_data_file.rfind('/')+1:market_data_file.rfind('.')]
  mtrans = []
  for t in trans:
    ticker, bdate, bprice, sdate, sprice = t
    assert bdate in m
    if sdate not in m:
      # This happens if the stock is dead before selling date and a somewhat random date is picked, which is not an open date.
      sdate, sprice = get_price_internal(m, sdate)
      if sdate is None or sprice is None:
        sdate = max_date
        sprice = m[sdate]
    else:
      sprice = m[sdate]
    mtrans.append([market, bdate, m[bdate], sdate, sprice])
  return mtrans

def get_gains(trans, real):
  gains = []
  for t in trans:
    ticker, bdate, bprice, sdate, sprice = t
    gain = (sprice - bprice) / bprice
    gains.append(gain)
  if real:
    # ASSUMPTION:
    # - $100 is spent on this stock
    # - IB charges $1+$1 per transaction
    gains = [g - 0.002 for g in gains]
  return gains

def get_string(trans, h, real):
  gains = sorted(get_gains(trans, real))
  avg_gain = sum(gains)/len(gains)*100
  POS = [0.01, 0.25, 0.5, 0.75, 0.99]
  pos = [gains[int(len(gains)*p)]*100 for p in POS]
  return '%d trans: avg = %.2f%%, %s | avg/day = %.2f%%' % (len(trans), avg_gain, ', '.join(['%d%% = %.2f%%' % (int(POS[i]*100), pos[i]) for i in range(len(POS))]), avg_gain/h)

def compute_sharpe_ratio(trans, mtrans, real):
  gains = get_gains(trans, real)
  mgains = get_gains(mtrans, False)
  assert len(gains) == len(mgains)
  diff = [gains[i] - mgains[i] for i in range(len(gains))]
  avg = sum(diff)/len(diff)
  var = [d - avg for d in diff]
  var = math.sqrt(sum([v*v for v in var])/len(var))
  return avg/var

