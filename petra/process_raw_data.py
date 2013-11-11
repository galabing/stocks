#!/usr/bin/python

import argparse
import os

MONTH_MAP = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12',
}

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()

  basenames = [f[:f.rfind('.')] for f in os.listdir(args.input_dir)
               if f.endswith('.txt')]
  print 'processing %d raw files: %s' % (len(basenames), basenames)

  for basename in basenames:
    input_file = '%s/%s.txt' % (args.input_dir, basename)
    output_file = '%s/%s.txt' % (args.output_dir, basename)
    with open(input_file, 'r') as fp:
      lines = fp.read().splitlines()
    assert len(lines) >= 2
    print 'processing %s' % lines[0]
    assert lines[1] == 'Date\tIndex Value\tStandard Error'
    output_lines = []
    for i in range(2, len(lines)):
      d, iv, se = lines[i].split('\t')
      m, y = d.split(' ')
      assert m in MONTH_MAP
      assert len(y) == 4 and int(y) > 1980 and int(y) < 2014
      d = '%s-%s' % (y, MONTH_MAP[m])
      iv, se = float(iv), float(se)
      output_lines.append('%s %f' % (d, iv))
    with open(output_file, 'w') as fp:
      for line in output_lines:
        print >> fp, line
    print '%d lines of output' % len(output_lines)

if __name__ == '__main__':
  main()

