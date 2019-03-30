import csv
import graphviz
import io
import math
import numpy
import random
import yaml

from docopt import docopt
from scipy.cluster.hierarchy import dendrogram, linkage  


class Interactions:
  """
  Each mapping contains a numerator and a denominator- because the numerator
  is always a subset of the demoninator, it gets added automatically during
  processing below. Additionally, because the numerators and denominators of
  +/- measures are the unions of their respective positive and negative
  measures, those get added during initialization. 

  RELATN measures:

  04 = 'conflict'
  05 = 'reinforcement'
  06 = 'independence'
  07 = 'conflict + reinforcement' (default)
  08 = 'conflict + independence'
  09 = 'reinforcement + independence'
  10 = '- conflict'
  11 = '- reinforcement'
  12 = '- independence'
  13 = '- conflict + reinforcement'
  14 = '- conflict + independence'
  14 = '- reinforcement + independence'
  16 = '+/- conflict'
  17 = '+/- reinforcement'
  18 = '+/- independence'
  19 = '+/- conflict + reinforcement'
  20 = '+/- conflict + independence'
  21 = '+/- reinforcement + independence'
  """

  mappings = {
    'conflict':                         {'n': set((('a_pos', 'b_neg'),
                                                   ('a_neg', 'b_pos'))),
                                         'd': set((('a_pos', 'b_nil'),
                                                   ('a_nil', 'b_pos')))},
    'reinforcement':                    {'n': set((('a_pos', 'b_pos'),)),
                                         'd': set((('a_pos', 'b_nil'),
                                                   ('a_pos', 'b_neg'),
                                                   ('a_neg', 'b_pos'),
                                                   ('a_nil', 'b_pos')))},
    'independence':                     {'n': set((('a_pos', 'b_nil'),
                                                   ('a_nil', 'b_pos'))),
                                         'd': set((('a_pos', 'b_neg'),
                                                   ('a_pos', 'b_pos'),
                                                   ('a_neg', 'b_pos')))},
    'conflict + reinforcement':         {'n': set((('a_pos', 'b_neg'),
                                                   ('a_pos', 'b_pos'),
                                                   ('a_neg', 'b_pos'))),
                                         'd': set((('a_pos', 'b_nil'),
                                                   ('a_nil', 'b_pos')))},
    'conflict + independence':          {'n': set((('a_pos', 'b_nil'),
                                                   ('a_pos', 'b_neg'),
                                                   ('a_neg', 'b_pos'),
                                                   ('a_nil', 'b_pos'))),
                                         'd': set((('a_pos', 'b_pos'),))},
    'reinforcement + independence':     {'n': set((('a_pos', 'b_nil'),
                                                   ('a_pos', 'b_pos'),
                                                   ('a_nil', 'b_pos'))),
                                         'd': set((('a_pos', 'b_neg'),
                                                   ('a_neg', 'b_pos')))},
    '- conflict':                       {'n': set((('a_pos', 'b_neg'),
                                                   ('a_neg', 'b_pos'))),
                                         'd': set((('a_neg', 'b_nil'),
                                                   ('a_neg', 'b_neg'),
                                                   ('a_nil', 'b_neg')))},
    '- reinforcement':                  {'n': set((('a_neg', 'b_neg'),)),
                                         'd': set((('a_neg', 'b_nil'),
                                                   ('a_pos', 'b_neg'),
                                                   ('a_neg', 'b_pos'),
                                                   ('a_nil', 'b_neg')))},
    '- independence':                   {'n': set((('a_neg', 'b_nil'),
                                                   ('a_nil', 'b_neg'))),
                                         'd': set((('a_pos', 'b_neg'),
                                                   ('a_neg', 'b_neg'),
                                                   ('a_neg', 'b_pos')))},
    '- conflict + reinforcement':       {'n': set((('a_pos', 'b_neg'),
                                                   ('a_neg', 'b_neg'),
                                                   ('a_neg', 'b_pos'))),
                                         'd': set((('a_neg', 'b_nil'),
                                                   ('a_nil', 'b_neg')))},
    '- conflict + independence':        {'n': set((('a_neg', 'b_nil'),
                                                   ('a_pos', 'b_neg'),
                                                   ('a_neg', 'b_pos'),
                                                   ('a_nil', 'b_neg'))),
                                         'd': set((('a_neg', 'b_neg'),))}, 
    '- reinforcement + independence':   {'n': set((('a_neg', 'b_nil'),
                                                   ('a_neg', 'b_neg'),
                                                   ('a_nil', 'b_neg'))),
                                         'd': set((('a_pos', 'b_neg'),
                                                   ('a_neg', 'b_pos')))},
    '+/- conflict':                     {'n': None, 
                                         'd': None},
    '+/- reinforcement':                {'n': None,
                                         'd': None},
    '+/- independence':                 {'n': None,
                                         'd': None},
    '+/- conflict + reinforcement':     {'n': None,
                                         'd': None},
    '+/- conflict + independence':      {'n': None,
                                         'd': None},
    '+/- reinforcement + independence': {'n': None,
                                         'd': None}
  }


  def __init__(self):
    """Initialize an interaction object.
    """
    for m in ('conflict', 'reinforcement', 'independence', 
              'conflict + reinforcement', 'conflict + independence',
              'reinforcement + independence'):
      self.mappings['+/- ' + m]['n'] = \
        self.mappings[m]['n'].union(self.mappings['- ' + m]['n'])
      self.mappings['+/- ' + m]['d'] = \
        self.mappings[m]['d'].union(self.mappings['- ' + m]['d'])

 
  def import_from_csv(self, csv_file):
    """Load data from a CSV file.

    :param csv_file: a file-like object.
    """
    reader = csv.reader(csv_file)

    self.variable_labels = next(reader, None)[1:]
    self.element_labels = []
    self.data = []

    data_mode = True
    for row in reader:
      if not any(row):
        if data_mode:
          data_mode = False
          continue
      else:
        if data_mode:
          self.element_labels.append(row[0])
          self.data.append([int(i) for i in row[1:]])
        else:
          self.weights = [int(i) for i in row[1:]]
          self.neg_min = [int(i) for i in next(reader, None)[1:]]
          self.pos_max = [int(i) for i in next(reader, None)[1:]]
          break


  def var_int(self, a, b, neg_min=-2, pos_max=2, a_neg=False, a_nil=False,
              a_pos=False, b_neg=False, b_nil=False, b_pos=False):
    """Get the unweighted interaction between two variables.
    
    :param float a:       a variable, from neg_min to pos_max.
    :param float b:       a variable, from neg_min to pos_max.
    :param float neg_min: minimum value for a or b.
    :param float pos_max: maximum value for a or b.
    :param bool a_neg:    return interactions where a < 0
    :param bool a_nil:    return interactions where a == 0
    :param bool a_pos:    return interactions where a > 0
    :param bool b_neg:    return interactions where b < 0
    :param bool b_nil:    return interactions where b == 0
    :param bool b_pos:    return interactions where b > 0

    :rtype float
    :returns the unweighted interaction between two variables, from 0.0 to 1.0
    inclusive.
    """
    assert sum((a_neg, a_nil, a_pos)) == 1
    assert sum((b_neg, b_nil, b_pos)) == 1

    if (a_neg and a >= 0.0) or (a_nil and a != 0) or (a_pos and a <= 0) or \
       (b_neg and b >= 0.0) or (b_nil and b != 0) or (b_pos and b <= 0):
      return 0.0

    r = 1.0 * pos_max - neg_min

    # Several of the functions below have been altered from the ones described
    # in Structured Planning on p. 137. Those formulas seem to produce results
    # outside of 0.0 to 1.0. The formulas below works for the chart on p. 140.
    # Several other formulas are best guesses- those are noted below.
    if (a_neg and b_nil) or (a_pos and b_nil):
      # altered from S.P. Negative case doesn't appear in S.P.
      return 1.0 - ((r / 2 - abs(a)) / (r / 2))
    elif a_pos and b_neg:
      return abs(a - b) / r
    elif (a_pos and b_pos) or (a_neg and b_neg):
      # altered from S.P. Negative case doesn't appear in S.P.
      return abs(a + b) / r
    elif a_neg and b_pos:
      return abs(a - b) / r
    elif (a_nil and b_pos) or (a_nil and b_neg):
      # altered from S.P. Negative case doesn't appear in S.P.
      return 1.0 - ((r / 2 - abs(b)) / (r / 2))


  def balance(self, a, b):
    """Get the balancing factor for two elements.
  
    :param int a: index of element a.
    :param int b: index of element b.

    :rtype float
    :returns the balancing factor.
    """
    supports_a = len([i for i in self.data[a] if i > 0])
    supports_b = len([i for i in self.data[b] if i > 0])
    return 1.0 * abs(supports_a - supports_b) / (supports_a + supports_b)


  def filtered_interaction(self, a, b, variation='conflict + reinforcement', filter=set()):
    """Get the weighted interaction between two elements.
  
    :param int a: index for element a.
    :param int b: index for element b.
    :param str variation: type of interaction. (see mappings.)
    :param set filter: elements to remove, for balancing equations. 
  
    :rtype float
    :returns the weighted interaction between two elements.
    """
    assert variation in self.mappings

    n = []
    d = []
    for i in range(0, len(self.weights)):
      kwargs_base = {
        'a': self.data[a][i],
        'b': self.data[b][i],
        'neg_min': self.neg_min[i],
        'pos_max': self.pos_max[i]
      }
      for a_arg, b_arg in self.mappings[variation]['n'].difference(filter):
        kwargs = {a_arg: True, b_arg: True}
        n.append(1.0 * self.weights[i] * self.var_int(
          **kwargs_base, **kwargs)
        )
        d.append(1.0 * self.weights[i] * math.ceil(self.var_int(
          **kwargs_base, **kwargs)
        ))
      for a_arg, b_arg in self.mappings[variation]['d'].difference(filter):
        kwargs = {a_arg: True, b_arg: True}
        d.append(1.0 * self.weights[i] * self.var_int(
          **kwargs_base, **kwargs))

    return 1.0 * sum(n) / sum(d)
  

  def interaction(self, a, b, variation='conflict + reinforcement'):
    """Get the interaction between two elements. Skew filters based on
       formulas on p. 143 of Structured Planning by Owens.
    """
    skew_a_filter = set((('a_neg', 'b_pos'),
                         ('a_nil', 'b_pos'),
                         ('a_nil', 'b_neg')))
    skew_b_filter = set((('a_neg', 'b_nil'),
                         ('a_pos', 'b_nil'),
                         ('a_pos', 'b_neg')))
    neutral = self.filtered_interaction(a, b, variation)
    skews_a = self.filtered_interaction(a, b, variation, skew_a_filter)
    skews_b = self.filtered_interaction(a, b, variation, skew_b_filter)
    b = self.balance(a, b)
    return (((1 - b) * neutral) + b * skews_a + b * skews_b) / (1 + b)


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
