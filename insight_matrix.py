#!/usr/bin/env python
"""Usage:
    insight_matrix build [--source=<format>] -
    insight_matrix cluster [--linkage_method=<linkage_method>] -
    insight_matrix fill [(--upper|--lower)] -
    insight_matrix graph_cluster [--engine=<engine>] -
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

import csv
import graphviz
import io
import numpy
import random
import sys
import yaml

from docopt import docopt
from scipy.cluster.hierarchy import dendrogram, linkage  


class Similarity:
  def __init__(self):
    self.records = None
    self.fields = None


  def load_yaml(self, f):
    """Load similarity data from a YAML file.

       Parameters:
         f -- a file-like object.
    """
    data = yaml.safe_load(f)
    self.records = data['records']
    self.fields = data['fields']


  def field_similarity(self, a, b, field):
    """Get an unweighted similarity score between two fields.

       Parameters:
         a -- a string, field label for the first record.
         b -- a string, field label for the second record.

       Returns: a float between 0.0 and 1.0, inclusive. 
    """
    if self.fields[field]['field_type'] == 'discrete':
      return float(self.records[a][field] == self.records[b][field])
    else:
      d = self.fields[field]['no_match_difference'] - \
          self.fields[field]['match_difference']
      n = self.fields[field]['no_match_difference'] - \
          abs(float(self.records[a][field]) - float(self.records[b][field]))
      if n < 0.0:
        n = 0.0
      if n > d:
        n = d
      return n / d

           
  def record_similarity(self, a, b):
    """Get a weighted similarity score between two records.

       Parameters:
         a -- a string, field label for the first record.
         b -- a string, field label for the second record.

       Returns: a float between 0.0 and 1.0, inclusive. 
    """
    scores = []
    for field in self.records[a].keys():
      scores.append(
        (
          self.field_similarity(a, b, field), 
          self.fields[field]['weight']
        )
      )

    match = sum([score * weight for score, weight in scores])
    no_match = sum([(1.0 - score) * weight for score, weight in scores])
    return match / (match + no_match)


  def csv(self):
    """Output a similarity matrix in CSV format.

       Returns: a string with CSV data.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    labels = sorted(self.records.keys())

    # x labels.
    writer.writerow([''] + labels)

    # y labels and data.
    for y, y_label in enumerate(labels):
      row = [labels[y]]
      for x_label in labels:
        row.append(self.record_similarity(y_label, x_label))
      writer.writerow(row)

    return output.getvalue()
    

class Matrix:
  def __init__(self):
    """Initialize the Matrix object.
    """
    self.x_labels = [] # list of strings.
    self.y_labels = [] # list of strings.
    self.data = None   # numpy.array or None.
                       # Elements should be floats from 0.0 to 1.0.


  def import_from_csv(self, csv_file):
    """Imports data and labels from a CSV file.
  
       Arguments:
       csv_file -- file-like object.
    """
    data = []

    reader = csv.reader(csv_file)
    self.x_labels = next(reader, None)[1:]

    for row in reader:
      self.y_labels.append(row[0])
      d = []
      for cell in row[1:]:
        try:
          d.append(float(cell))
        except ValueError:
          d.append(0.0)
      data.append(d)
      self.data = numpy.array(data)


  def width(self):
    return self.data.shape[1]


  def height(self):
    return self.data.shape[0]
    

  def max(self):
    """Returns:
       A float, the maximum value in the matrix. 
    """
    return max(self.data.reshape(-1,).tolist())


  def is_symmetric(self):
    """Check to be sure a matrix is symmetric. 
  
       Returns: boolean.
    """
    if self.width() != self.height():
      return False

    if self.x_labels != self.y_labels:
      return False

    for x, y in self.get_symmetric_index_pairs():
      if self.data[y, x] != self.data[x, y]:
        return False
    return True
   
 
  def get_symmetric_index_pairs(self, upper=True):
    """Get all the index pairs necessary for a symmetric matrix,
       for either the upper or lower triangle of the matrix. 

       Arguments:
       upper -- a boolean, if True return indices for an upper triangle, if
                False return indices for a lower triangle.

       Returns:
       A list of index pairs. 
    """
    assert self.width() == self.height()

    if upper:
      return list(zip(*numpy.triu_indices(self.width())))
    else:
      return list(zip(*numpy.tril_indices(self.width())))


  def scale(self):
    raise NotImplementedError


  def fill(self, upper=True):
    """Fill in a symmetric matrix by copying the upper triangle to the lower
       triangle, or vice versa.

       Arguments:
       upper -- a boolean. Fill the upper triangle if true, fill the lower
                triangle if false.
  
       Side effect:
       Fills in the matrix. 
    """
    assert self.width() == self.height()

    for x, y in self.get_symmetric_index_pairs(upper):
      self.data[x, y] = self.data[y, x]
  
  
  def reorder(self, y_order, x_order=None):
    """Reorder the matrix.
  
       Arguments:
       y_order -- a list of indices: the new y matrix order.
       x_order -- a list of indices: the new x matrix order, or None for
                  symmetric matrices. 
  
       Side effect:
       Reorder data.
    """
    if self.is_symmetric():
      x_order = y_order
    assert x_order is not None

    # reorder labels.
    self.y_labels = [self.y_labels[i] for i in y_order]
    self.x_labels = [self.x_labels[i] for i in x_order]

    # reorder data.
    new_data = numpy.empty((self.height(), self.width()))
    for y in range(self.height()):
      for x in range(self.width()):
        new_data[y, x] = self.data[y_order[y], x_order[x]]
    self.data = new_data


  def cluster(self, linkage_method='complete'):
    """Cluster similarity/distance data to get a new index order.
  
       Arguments:
       linkage_method -- e.g., 'single', 'complete', 'average', 'weighted',
                         'median', 'ward', see
                         https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html.
    """
    index_order = dendrogram(
      linkage(self.data, linkage_method),
      distance_sort='descending',
      no_plot=True,
      orientation='top',
      show_leaf_counts=True
    )['leaves']
    self.reorder(index_order)


  def randomize(self):
    """Randomize the matrix, e.g. for testing. 
  
       Side effect:
       Puts matrix elements in a random order.
    """
    y_indices = list(range(self.height()))
    random.shuffle(y_indices)
    if self.is_symmetric():
      self.reorder(y_indices)
    else:
      x_indices = list(range(self.width()))
      random.shuffle(x_indices)
      self.reorder(y_indices, x_indices)


  def csv(self):
    """Exports data and labels to a CSV string.

       Returns:
       a string, CSV data.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # x labels.
    writer.writerow([''] + self.x_labels)    

    # y labels and data.
    for y, row in enumerate(self.data.tolist()):
      writer.writerow([self.y_labels[y]] + row)

    return output.getvalue()


  def ascii(self):
    """Returns:
       A string, an ASCII-art representation of the matrix and labels.
    """
    to_ascii = numpy.vectorize(lambda c: ' .,:-=+*#%@'[int(c * 10)])

    max_x_label_size = max([len(l) for l in self.x_labels])
    max_y_label_size = max([len(l) for l in self.y_labels])

    # build a 2d array of double spaces with enough room for x and y labels. 
    output = [['  ' for i in range(max_y_label_size + 1 + self.width())] for j in range(max_x_label_size + 1 + self.height())]

    # add x labels.
    for x, l in enumerate(self.x_labels):
      label_size = len(l)
      for y, c in enumerate(l):
        output[max_x_label_size - label_size + y][max_y_label_size + 1 + x] = ' ' + c

    # add y labels.
    for y, l in enumerate(self.y_labels):
      label_size = len(l)
      for x, c in enumerate(l):
        output[max_x_label_size + 1 + y][(max_y_label_size - label_size) + x] = ' ' + c

    # add data.
    for y, row in enumerate(self.data.tolist()):
      for x, cell in enumerate(row):
        output[max_x_label_size + 1 + y][max_y_label_size + 1 + x] = ' ' + ' .,:-=+*#%@'[int(cell * 10)]

    return '\n'.join([''.join(r) for r in output]) + '\n'


  def graph(self, cutoff, engine):
    g = graphviz.Graph(engine=engine)
    g.attr(overlap='false')
    for x, y in self.get_symmetric_index_pairs():
      if x == y:
        continue
      if self.data[y, x] >= cutoff:
        g.edge(self.y_labels[y], self.x_labels[x])
    g.view()


if __name__ == '__main__':
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
