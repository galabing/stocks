#!/usr/bin/python

import argparse

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--libsvm_output_file', required=True)
  parser.add_argument('--libsvm_meta_file', required=True)
  parser.add_argument('--metadata_file', required=True)
  parser.add_argument('--num', required=True)
  parser.add_argument('--output_file', required=True)
  parser.add_argument('--short', action='store_true')
  args = parser.parse_args()

  num = int(args.num)
  assert num > 0

  with open(args.libsvm_meta_file, 'r') as fp:
    meta_keys = fp.read().splitlines()
  date_map = dict()
  for key in meta_keys:
    t, d = key.split(' ')
    if d not in date_map:
      date_map[d] = []
    date_map[d].append(key)

  with open(args.libsvm_output_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(meta_keys) == len(lines) - 1
  assert lines[0] == 'labels 1 -1'
  items = []
  prob_map = dict()
  for i in range(1, len(lines)):
    l, p, n = lines[i].split(' ')
    l, p, n = int(l), float(p), float(n)
    assert l == 1 or l == -1
    assert abs(p + n - 1) < 1e-5
    if args.short:
      p, n = n, p
    key = meta_keys[i-1]
    items.append([key, p])
    t, d = key.split(' ')
    if d not in prob_map:
      prob_map[d] = []
    prob_map[d].append([t, p])
  items.sort(key=lambda item: item[1], reverse=True)

  print 'loaded %d predicted items with high: %f, low: %f, mean: %f' % (
      len(items), items[0][1], items[-1][1],
      sum([items[i][1] for i in range(len(items))])/len(items))

  with open(args.metadata_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(meta_keys) <= len(lines) - 1
  meta_set = set(meta_keys)
  meta_map = dict()
  for i in range(1, len(lines)):
    d, t, l, g, r = lines[i].split(' ')
    key = '%s %s' % (t, d)
    if key not in meta_set:
      continue
    assert key not in meta_map
    assert l == '+1' or l == '-1'
    assert g[-1] == '%'
    g = float(g[:-1])/100
    meta_map[key] = g
  assert set(meta_map.keys()) == meta_set

  output = []
  for date in sorted(date_map.keys()):
    probs = prob_map[date]
    probs.sort(key=lambda prob: prob[1], reverse=True)
    m = min(len(probs), num)
    skeys = ['%s %s' % (probs[i][0], date) for i in range(m)]
    keys = date_map[date]
    sg = [meta_map[k] for k in skeys]
    ag = [meta_map[k] for k in keys]
    if len(sg) == 0:
      asg = 0.0
    else:
      asg = sum(sg)/len(sg)
    assert len(ag) > 0
    output.append([date, asg, sum(ag)/len(ag), len(sg), len(ag)])

  with open(args.output_file, 'w') as fp:
    print >> fp, 'date,pick_gain,market_gain,pick_size,market_size'
    spg, smg, sps, sms = 0.0, 0.0, 0, 0
    for o in output:
      d, pg, mg, ps, ms = o
      spg += pg
      smg += mg
      sps += ps
      sms += ms
      print >> fp, '%s,%.4f%%,%.4f%%,%d,%d' % (d, pg*100, mg*100, ps, ms)
    print >> fp, 'sum,%.4f%%,%.4f%%,%d,%d' % (spg*100, smg*100, sps, sms)
    print >> fp, 'avg,%.4f%%,%.4f%%,%.2f,%.2f' % (
        spg*100/len(output), smg*100/len(output),
        float(sps)/len(output), float(sms)/len(output))

if __name__ == '__main__':
  main()

