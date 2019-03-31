#!/usr/bin/env python
"""Usage:
    insight_matrix build [--source=<format>] -
    insight_matrix cluster [--linkage_method=<linkage_method>] -
    insight_matrix fill [(--upper|--lower)] -
    insight_matrix graph_cluster [--engine=<engine>] -
    insight_matrix histogram -
    insight_matrix randomize -
    insight_matrix show -
    insight_matrix (--help)

   Arguments:
    engine:         dot
                    neato
                    fdp
                    twopi
                    circo

    linkage_method: single
                    complete
                    average
                    weighted
                    median
                    ward

    source:         yaml
"""

import sys

from docopt import docopt
from classes import Matrix


def main():
  options = docopt(__doc__)

  if options['build']:
    s = Similarity()
    s.load_yaml(sys.stdin)
    sys.stdout.write(s.csv())
    sys.exit()
  elif options['cluster']:
    m = Matrix()
    if '-' in options:
      m.import_from_csv(sys.stdin)
    if options['--linkage_method']:
      m.cluster(options['--linkage_method'])
    else:
      m.cluster()
  elif options['fill']:
    m = Matrix()
    if '-' in options:
      m.import_from_csv(sys.stdin)
    if options['--upper']:
      m.fill(True)
    elif options['--lower']:
      m.fill(False)
  elif options['graph_cluster']:
    m = Matrix()
    if '-' in options:
      m.import_from_csv(sys.stdin)
    m.graph(0.5, options['--engine'])
  elif options['histogram']:
    m = Matrix()
    if '-' in options:
      m.import_from_csv(sys.stdin)
      m.histogram()
      sys.exit()
  elif options['randomize']:
    m = Matrix()
    if '-' in options:
      m.import_from_csv(sys.stdin)
    m.randomize()
  elif options['show']:
    m = Matrix()
    if '-' in options:
      m.import_from_csv(sys.stdin)
    sys.stdout.write(m.ascii())
    sys.exit()
  sys.stdout.write(m.csv())
  sys.exit()


if __name__ == '__main__':
  main()
