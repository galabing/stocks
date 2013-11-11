#!/usr/bin/python

import argparse

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_file', required=True)
  parser.add_argument('--ranges', required=True)
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()

  indices = [int(index) for index in args.ranges.split(',')]
  assert len(indices) % 2 == 0
  for i in range(0, len(indices), 2):
    assert indices[i] > 0
    assert indices[i+1] >= indices[i]
    if i > 0:
      assert indices[i] > indices[i-1]

  ifp = open(args.input_file, 'r')
  ofp = open(args.output_file, 'w')

  n = None
  while True:
    line = ifp.readline()
    if line == '':
      break
    assert line.startswith('+1 ') or line.startswith('-1 ')
    assert line.endswith('\n')
    label = line[:2]
    items = line[3:-1].split(' ')
    if n is None:
      n = len(items)
    else:
      assert n == len(items)
    assert n >= indices[-1]
    values = []
    for j in range(0, len(indices), 2):
      for i in range(indices[j]-1, indices[j+1]):
        index, value = items[i].split(':')
        assert int(index) == i+1
        values.append(float(value))
    print >> ofp, '%s %s' % (
        label,
        ' '.join(['%d:%f' % (i+1, values[i]) for i in range(len(values))]))

  ifp.close()
  ofp.close()

if __name__ == '__main__':
  main()

