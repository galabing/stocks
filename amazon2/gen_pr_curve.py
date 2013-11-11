#!/usr/bin/python

import argparse

RECALL_STEP = 0.0001

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--libsvm_output_file', required=True)
  parser.add_argument('--libsvm_meta_file', required=True)
  parser.add_argument('--metadata_file', required=True)
  parser.add_argument('--output_file', required=True)
  parser.add_argument('--short', action='store_true')
  args = parser.parse_args()

  with open(args.libsvm_meta_file, 'r') as fp:
    meta_keys = fp.read().splitlines()

  with open(args.libsvm_output_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(meta_keys) == len(lines) - 1
  assert lines[0] == 'labels 1 -1'
  items = []
  for i in range(1, len(lines)):
    l, p, n = lines[i].split(' ')
    l, p, n = int(l), float(p), float(n)
    assert l == 1 or l == -1
    assert abs(p + n - 1) < 1e-5
    if args.short:
      items.append([meta_keys[i-1], n])
    else:
      items.append([meta_keys[i-1], p])
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
    d, t, l, _, _ = lines[i].split(' ')
    key = '%s %s' % (t, d)
    if key not in meta_set:
      continue
    assert key not in meta_map
    assert l == '+1' or l == '-1'
    if l == '+1':
      s = 1
    else:
      s = 0
    meta_map[key] = s
  assert set(meta_map.keys()) == meta_set

  tp, fp = 0, 0
  if not args.short:
    fn = sum(meta_map.values())
    tn = len(meta_map) - fn
  else:
    tn = sum(meta_map.values())
    fn = len(meta_map) - tn
  print 'starting with tp: %d, fp: %d, tn: %d, fn: %d' % (tp, fp, tn, fn)
  next_recall = 0.0
  output = []
  for i in range(len(items)):
    key, prob = items[i]
    label = meta_map[key]
    if (not args.short and label == 1) or (args.short and label == 0):
      tp += 1
      fn -= 1
    else:
      assert (not args.short and label == 0) or (args.short and label == 1)
      fp += 1
      tn -= 1
    precision = float(tp)/(tp+fp)
    recall = float(tp)/(tp+fn)
    if recall >= next_recall:
      output.append([precision, recall, prob, i+1, len(items)-i-1])
      while next_recall <= recall:
        next_recall += RECALL_STEP
  print 'ending with tp: %d, fp: %d, tn: %d, fn: %d' % (tp, fp, tn, fn)

  with open(args.output_file, 'w') as fp:
    print >> fp, 'precision,recall,threshold,above,below'
    for o in output:
      p, r, t, a, b = o
      print >> fp, '%.4f%%,%.4f%%,%.4f,%d,%d' % (p*100, r*100, t, a, b)

if __name__ == '__main__':
  main()

