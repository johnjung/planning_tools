import csv
import graphviz
import io
import numpy
import random
import re
import xml.etree.ElementTree as ElementTree

from docopt import docopt
from scipy.cluster.hierarchy import dendrogram, linkage


class CardSort:
    """Build a similarity matrix from card sort data.

    Notes:
        Record card sort data in a .csv file with three columns:

        field 1) participant identifier.
        field 2) group identifier.
        field 3) item.

        Taken together, fields 1 and 2 should uniquely identify a row in the
        input data. This code works for both closed card sorts, where group
        names are determined before test time, and open card sorts, where
        participants choose their own groups. Groups can be named (e.g. "citrus
        fruits", "starchy vegetables", etc.) but the algorithm for determining
        similarity will ignore group names.

        Within an indiviual test, items can be placed in multiple groups. If 
        a participant forms a group of items that don't fit into any other
        group, they should be excluded rather than placed into a
        "miscellaneous" group.

    Example:
        A,01,sherry
        A,02,tobacco
        A,02,leather
        B,01,confiture
        B,02,yarrow
        B,03,celery
        C,01,onion
        C,02,confiture
        C,03,yarrow

        The data above records groupings from three different participants: A,
        B and C. Participant A created two different groups, labelled '01' and
        '02' here. Group '01' contains a single item (sherry) and group '02'
        contains two items: tobacco and leather. Participants B and C each
        created three groups, labelled '01', '02', and '03', which are distinct
        from each other and the groups created by participant A.

    References:
        Jaccard index: https://en.wikipedia.org/wiki/Jaccard_index
    """

    def __init__(self):
        """Constructor

        Notes:
            The tests property is a dictionary for representing card sort data:
            e.g.:
                {
                  'participant A': {
                    'group 1': set(('item i', 'item ii')),
                    'group 2': set(('item iii',))
                  },
                  'participant B': {
                    'group 1': set(('item i',)),
                    'group 2': set(('item ii', 'item iii'))
                  }
                }
        """
        self.tests = {}

    def import_from_csv(self, csv_file):
        """Load data from a CSV file.

        Args:  
            csv_file: a file-like object.
        """
        reader = csv.reader(csv_file)

        for f in reader:
            assert len(f) == 3 and all(f)
            if not f[0] in self.tests:
                self.tests[f[0]] = {}
            if not f[1] in self.tests[f[0]]:
                self.tests[f[0]][f[1]] = set()
            self.tests[f[0]][f[1]].add(f[2])

    def get_groups(self):
        """Get a flat list of sets, all groups from all tests. e.g.:
        [
        set(('item 1',)),
        set(('item 2', 'item 3')),
        ...
        ]

        Returns:
            list: a list of sets.
        """
        return [g for t in self.tests.values() for g in t.values()]

    def get_elements(self):
        """Get a sorted list of unique elements that appeared in any tests, e.g.:
        ['apples', 'bananas', 'oranges']

        Returns:
            list: a unique list of elements from the card sort.
        """
        return sorted(set([e for g in self.get_groups() for e in g]))

    def get_jaccard(self, a, b):
        """Get the Jaccard index of two elements.

        Args:
            a (str): an element from the card sort.
            b (str): an element from the card sort.

        Returns:
            float: a number between 0.0 and 1.0, inclusive.
        """
        elements = set([a, b])
        counts = []
        for g in self.get_groups():
            counts.append(len(elements.intersection(g)))
        return 1.0 * \
            len([c for c in counts if c == 2]) / \
            len([c for c in counts if c >= 1])

    def get_lower_triangle_indices(self):
        """Get indices for the lower triangle of a matrix, e.g.:
        [(1, 0), (2, 0), (2, 1)]

        Returns:
            list: a list of tuples.
        """
        elements = self.get_elements()
        return [(y, x) for y in range(len(elements)) for x in range(y)]

    def get_similarity_data(self):
        """Get a two-dimensional list of similarity data.

        Returns:
            list: a list of lists, where each row contains similarity data
            (floats) from 0.0 to 1.0
        """
        elements = self.get_elements()
        data = [['' for i in range(len(elements))]
                for j in range(len(elements))]

        for i in range(len(elements)):
            data[i][i] = 1.0

        for y, x in self.get_lower_triangle_indices():
            j = self.get_jaccard(elements[x], elements[y])
            data[y][x] = j

        return data

    def csv(self):
        """Get CSV output as a string."""
        output = io.StringIO()
        writer = csv.writer(output)
        labels = sorted(list(self.get_elements()))
        data = self.get_similarity_data()

        writer = csv.writer(output)
        writer.writerow([''] + labels)
        for y in range(len(data)):
            writer.writerow([labels[y]] + data[y])

        return output.getvalue()


class Interactions:
    """Build a matrix of similarity data for two different sets: e.g.,
    requirements and project features.

    The code is designed to reveal affinities and tensions between different
    things in the planning process: for example, if low cost and comfort are
    both user requirements for a trip on an airplane, a measure of conflict 
    might reveal "seating leg room" as a trouble spot.

    The mappings in this class each contain a numerator and a denominator,
    labelled 'n' and 'd'. Because the numerator is always a subset of the 
    denominator, it gets added automatically during processing below.
    Additionally, because the numerators and denominators of +/- measures are
    the unions of their respective positive and negative measures, those get
    added during initialization. 

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
        """Constructor"""
        for m in ('conflict', 'reinforcement', 'independence',
                  'conflict + reinforcement', 'conflict + independence',
                  'reinforcement + independence'):
            self.mappings['+/- ' + m]['n'] = \
                self.mappings[m]['n'].union(self.mappings['- ' + m]['n'])
            self.mappings['+/- ' + m]['d'] = \
                self.mappings[m]['d'].union(self.mappings['- ' + m]['d'])

    def import_from_csv(self, csv_file):
        """Load data from a CSV file.

        Args:
            csv_file: a file-like object.
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

        Args:
            a (float):       a variable, from neg_min to pos_max.
            b (float):       a variable, from neg_min to pos_max.
            neg_min (float): minimum value for a or b.
            pos_max (float): maximum value for a or b.
            a_neg (bool):    return interactions where a < 0
            a_nil (bool):    return interactions where a == 0
            a_pos (bool):    return interactions where a > 0
            b_neg (bool):    return interactions where b < 0
            b_nil (bool):    return interactions where b == 0
            b_pos (bool):    return interactions where b > 0

        Returns:
            float: the unweighted interaction between two variables, from 0.0
            to 1.0 inclusive.
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

        Args:
            a (int): index of element a.
            b (int): index of element b.

        Returns:
            float: the balancing factor.
        """
        supports_a = len([i for i in self.data[a] if i > 0])
        supports_b = len([i for i in self.data[b] if i > 0])
        return 1.0 * abs(supports_a - supports_b) / (supports_a + supports_b)

    def filtered_interaction(self, a, b, variation='conflict + reinforcement', filter=set()):
        """Get the weighted interaction between two elements.

        Args:
            a (int): index for element a.
            b (int): index for element b.
            variation (str): type of interaction. (see mappings.)
            filter (set): elements to remove, for balancing equations. 

        Returns:
            float: the weighted interaction between two elements.
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
                d.append(1.0 * self.weights[i] * float(bool(self.var_int(
                    **kwargs_base, **kwargs)
                )))
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
    """Build a similarity matrix from fielded data.

    Notes:
        This class takes a .csv as input and produces a similarity matrix as
        output. CSV data for input should include one record per row. Fields
        may be continuous data, like floating point numbers from 0.0 to 1.0;
        discrete data, like integers from 1 to 10; or categorical data, like 
        'suv', 'compact', 'sport', or 'sedan'.

        Weights can be assigned to different fields to alter their relative
        importance. 
    """
    def __init__(self):
        """Constructor"""
        self.records = None
        self.fields = None

    def import_from_csv(self, csv_file):
        """Load similarity data from a .csv file.

        Args:
            csv_file: a file-like object.
        """
        reader = csv.reader(csv_file)
        fields = next(reader, None)[1:]
        self.fields = {f: {} for f in fields}
        self.records = {}

        data_mode = True
        for row in reader:
            if not any(row):
                if data_mode:
                    data_mode = False
                    continue
            else:
                if data_mode:
                    self.records[row[0]] = {}
                    for f in range(len(fields)):
                        if re.match('^[0-9]+$', row[f + 1]):
                            self.records[row[0]][fields[f]] = int(row[f + 1])
                        elif re.match('^[0-9.]+$', row[f + 1]):
                            self.records[row[0]][fields[f]] = float(row[f + 1])
                        else:
                            self.records[row[0]][fields[f]] = row[f + 1]
                else:
                    for f in range(len(fields)):
                        if re.match('^[0-9]+$', row[f + 1]):
                            self.fields[fields[f]][row[0]] = int(row[f + 1])
                        elif re.match('^[0-9.]+$', row[f + 1]):
                            self.fields[fields[f]][row[0]] = float(row[f + 1])
                        else:
                            self.fields[fields[f]][row[0]] = row[f + 1]

    def field_similarity(self, a, b, field):
        """Get an unweighted similarity score between two fields.

        Args:
            a (str): a field label for the first record.
            b (str): a field label for the second record.

        Returns:
            float: a number between 0.0 and 1.0, inclusive. 
        """
        if self.fields[field]['field_type'] == 'discrete':
            return float(self.records[a][field] == self.records[b][field])
        else:
            d = self.fields[field]['no_match_difference'] - \
                self.fields[field]['match_difference']
            n = self.fields[field]['no_match_difference'] - \
                abs(float(self.records[a][field]) -
                    float(self.records[b][field]))
            if n < 0.0:
                n = 0.0
            if n > d:
                n = d
            return n / d

    def record_similarity(self, a, b, mode='01'):
        """Get a weighted similarity score between two records.

        Args:
            a (str): a field label for the first record.
            b (str): a field label for the second record.
            mode (str): alternate formulas for calculating similarity, see S.P.
            p. 157.

        Returns:
            float: a float between 0.0 and 1.0, inclusive. 
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

        if mode == '01':
            return match / (match + no_match)
        elif mode == '02':
            return match / (match + 2 * no_match)
        elif mode == '03':
            return 2 * match / (2 * match + no_match)
        else:
            raise ValueError

    def csv(self):
        """Output a similarity matrix in CSV format.

        Returns:
            str: a string with CSV data.
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
    """A class to manipulate matrix objects.

    Notes:
        This class includes methods to manipulate matrices of data, e.g. by 
        clustering and sorting them. It uses scipy to produce a dendrogram
        for sorting information.
    """
    def __init__(self):
        """Initialize the Matrix object.
        """
        self.x_labels = []  # list of strings.
        self.y_labels = []  # list of strings.
        self.data = None   # numpy.array or None.
        # Elements should be floats from 0.0 to 1.0.

    def import_from_csv(self, csv_file):
        """Imports data and labels from a CSV file.

        Args:
            csv_file: a file-like object.
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
        self.fill()

    def width(self):
        return self.data.shape[1]

    def height(self):
        return self.data.shape[0]

    def max(self):
        """
        Returns:
            float: the maximum value in the matrix.
        """
        return max(self.data.reshape(-1,).tolist())

    def is_symmetric(self):
        """Check to be sure a matrix is symmetric. 

        Returns:
            bool
        """
        if self.width() != self.height():
            return False
        if self.x_labels != self.y_labels:
            return False
        return True

    def get_symmetric_index_pairs(self, upper=True):
        """Get all the index pairs necessary for a symmetric matrix,
           for either the upper or lower triangle of the matrix. 

        Args:
            upper (bool): if True return indices for an upper triangle, if
            False return indices for a lower triangle.

        Returns:
            list: index pairs. 
        """
        assert self.width() == self.height()

        if upper:
            return list(zip(*numpy.triu_indices(self.width())))
        else:
            return list(zip(*numpy.tril_indices(self.width())))

    def scale(self):
        raise NotImplementedError

    def fill(self, upper=True):
        """Fill in a symmetric matrix by copying the lower triangle to the
        upper triangle, or vice versa.

        Args:
            upper (bool): Fill the upper triangle if true, fill the lower
            triangle if false.
        """
        if self.is_symmetric():
            for x, y in self.get_symmetric_index_pairs(upper):
                self.data[x, y] = self.data[y, x]

    def reorder(self, y_order, x_order=None):
        """Reorder the matrix.

        Args:
            y_order (list): indices for the new y matrix order.
            x_order (list): indices for the new x matrix order, or None for
                            symmetric matrices. 
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

        Args:
            linkage_method (str): e.g., 'single', 'complete', 'average',
            'weighted', 'median', 'ward', see
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
        """Randomize the matrix, e.g. for testing."""
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
           str: returns CSV data.
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
        """
        Returns:
           str: an ASCII-art representation of the matrix and labels.
        """
        to_ascii = numpy.vectorize(lambda c: ' .,:-=+*#%@'[int(c * 10)])

        max_x_label_size = max([len(l) for l in self.x_labels])
        max_y_label_size = max([len(l) for l in self.y_labels])

        # build a 2d array of double spaces with enough room for x and y labels.
        output = [['  ' for i in range(max_y_label_size + 1 + self.width())]
                  for j in range(max_x_label_size + 1 + self.height())]

        # add x labels.
        for x, l in enumerate(self.x_labels):
            label_size = len(l)
            for y, c in enumerate(l):
                output[max_x_label_size - label_size +
                       y][max_y_label_size + 1 + x] = ' ' + c

        # add y labels.
        for y, l in enumerate(self.y_labels):
            label_size = len(l)
            for x, c in enumerate(l):
                output[max_x_label_size + 1 +
                       y][(max_y_label_size - label_size) + x] = ' ' + c

        # add data.
        for y, row in enumerate(self.data.tolist()):
            for x, cell in enumerate(row):
                output[max_x_label_size + 1 + y][max_y_label_size +
                                                 1 + x] = ' ' + ' .,:-=+*#%@'[int(cell * 10)]

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

    def histogram(self):
        coefficients = []
        for y, x in self.get_symmetric_index_pairs(upper=False):
            coefficients.append(self.data[y, x])

        count, bin_start = numpy.histogram(
            coefficients, bins=101, range=(0.0, 1.0))
        total = sum(count)

        # histogram max is the largest non-zero bin.
        h_max = max(count[1:])

        i = 0
        total_count = 0
        while i < len(bin_start) - 1:
            print('{:.2f}: {} {}'.format(
                bin_start[i],
                count[i],
                1.0 * count[i] / total_count
            ))
            total_count = total_count + count[i]
            i = i + 1

    def svg(self):
        def draw_cell(x, y):
            cell_size = (self.chart_width - self.cell_spacing *
                         (len(self.data) - 1)) / len(self.data)
            x_offset = cell_size * x + (self.cell_spacing * (x - 1))
            y_offset = cell_size * y + (self.cell_spacing * (y - 1))
            ElementTree.SubElement(
                svg,
                'rect',
                x=x_offset,
                y=y_offset,
                width=str(cell_size),
                height=str(cell_size),
                style="fill: black"
            )
        svg = ElementTree.Element(
            'svg',
            width=str(self.chart_width),
            height=str(self.chart_height),
            version='1.1'
        )
        for y in range(len(self.data)):
            for x in range(len(self.data[0])):
                draw_cell(x, y)
