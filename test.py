import unittest
from insight_matrix import Matrix


class TestMatrix(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.symmetric_matrix = Matrix()
    f = open('test_data/symmetric.csv')
    self.symmetric_matrix.import_from_csv(f)
    f.close()

    self.nonsymmetric_matrix = Matrix()
    f = open('test_data/nonsymmetric.csv')
    self.nonsymmetric_matrix.import_from_csv(f)
    f.close()
 
 
  def test_import_from_csv(self):
    """import should work correctly.
    """
    self.assertTrue(len(self.symmetric_matrix.x_labels) == 3)
    self.assertTrue(len(self.symmetric_matrix.y_labels) == 3)
    self.assertEqual(self.symmetric_matrix.data.shape, (3, 3))

    self.assertEqual(self.nonsymmetric_matrix.x_labels, ['cheap', 'good'])
    self.assertEqual(self.nonsymmetric_matrix.y_labels, ['aldi', 'trader joes', 'whole foods'])
    self.assertEqual(self.nonsymmetric_matrix.data.shape, (3, 2))

 
  def test_width(self):
    self.assertEqual(self.nonsymmetric_matrix.width(), 2)


  def test_height(self):
    self.assertEqual(self.nonsymmetric_matrix.height(), 3)


  def test_max(self):
    self.assertEqual(self.symmetric_matrix.max(), 1.0)
    self.assertEqual(self.nonsymmetric_matrix.max(), 1.0)


  def test_is_symmetric(self):
    """is_symmetric() should correctly identify symmetric matrices.
    """
    self.assertTrue(self.symmetric_matrix.is_symmetric())
    self.assertFalse(self.nonsymmetric_matrix.is_symmetric())


  def test_get_symmetric_index_pairs(self):
    self.assertEqual(
      self.symmetric_matrix.get_symmetric_index_pairs(True),
      [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
    )
    self.assertEqual(
      self.symmetric_matrix.get_symmetric_index_pairs(False),
      [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2)]
    )


  def test_randomize(self):
    fruits_and_vegetables = Matrix()
    f = open('sample_data/fruits_and_vegetables.csv')
    fruits_and_vegetables.import_from_csv(f)
    f.close()

    self.assertEqual(
      fruits_and_vegetables.x_labels,
      fruits_and_vegetables.y_labels
    )
 

if __name__ == '__main__':    
  unittest.main()
