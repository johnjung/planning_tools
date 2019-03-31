import csv
import sys


class CardSort:
  def __init__(self):
    """
    Tests is a dictionary, where keys are the names of each test and values are
    the groupings from each test. Groups are also represented as dictionaries-
    here the key is the name of each group and the value is a set of elements.
    """
    self.tests = {}

  def import_from_csv(self, csv_file):
    """Load data from a CSV file.

    :param csv_file: a file-like object.
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
    """Get a flat list of sets, all groups from all tests.
    """
    return [g for t in self.tests.values() for g in t.values()]


  def get_elements(self):
    """Get a sorted list of unique elements that appeared in any tests.
    """
    return sorted(set([e for g in self.get_groups() for e in g]))
  

  def get_jaccard(self, a, b):
    """Intersection over union.
    """
    elements = set([a, b])
    counts = []
    for g in self.get_groups():
      counts.append(len(elements.difference(g)))
    return 1.0 * \
           len([c for c in counts if c >= 1]) / \
           len([c for c in counts if c == 2])


  def get_lower_triangle_indices(self):
    """e.g., [(1, 0), (2, 0), (2, 1)]
    """
    elements = self.get_elements()
    return [(y, x) for y in range(len(elements)) for x in range(y)]


  def get_similarity_data(self):
    """Return a two-dimensional list of similarity data.
    """
    elements = self.get_elements()
    data = [[[] for i in range(len(elements))] for j in range(len(elements))]

    for i in range(len(elements)):
      data[i][i] = 1.0

    for y, x in self.get_lower_triangle_indices():
      j = self.get_jaccard(elements[x], elements[y])
      data[y][x] = j
      data[x][y] = j

    return data


  def to_csv(self, f):
    labels = sorted(list(self.get_elements()))
    data = self.get_similarity_data()

    writer = csv.writer(f)
    writer.writerow([] + labels)
    for y in range(len(data)):
      writer.writerow([labels[y]] + data[y])


def main():
  c = CardSort()
  c.import_from_csv(sys.stdin)
  c.to_csv(sys.stdout)


if __name__=='__main__':
  main()
