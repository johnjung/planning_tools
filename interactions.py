import csv
import math
import sys

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
    if a_pos and b_nil:
      # altered from S.P.
      return 1.0 - ((r / 2 - a) / (r / 2))
    elif a_pos and b_neg:
      return abs(a - b) / r
    elif a_pos and b_pos:
      # altered from S.P.
      return (a + b) / r
    elif a_neg and b_pos:
      return abs(a - b) / r
    elif a_nil and b_pos:
      # altered from S.P.
      return 1.0 - ((r / 2 - b) / (r / 2))
    else:
      raise ValueError


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
    """Get the interaction between two elements. I don't grok how balancing
    works when the variation isn't conflict + reinforcement, so I'll leave that
    to implement later.
    """
    if variation == 'conflict + reinforcement':
      neutral = self.filtered_interaction(a, b, variation)
      skews_a = self.filtered_interaction(a, b, variation, set((('a_neg', 'b_pos'),
                                                                ('a_nil', 'b_pos'))))
      skews_b = self.filtered_interaction(a, b, variation, set((('a_pos', 'b_nil'),
                                                                ('a_pos', 'b_neg'))))
      balance = self.balance(a, b)
      return (((1 - balance) * neutral) + balance * skews_a + balance * skews_b) / (1 + balance)
    else:
      return self.filtered_interaction(a, b, variation)
