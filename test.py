import unittest
from index.py import validate_worksheet

class TestInsightMatrix(unittest.TestCase):
  def test_correct_matrix_with_labels(self):
    """A correctly formed matrix should validate without raising an exception.
    """
    try:
      validate_worksheet(self.load_worksheet('test_data/correct_matrix_with_labels.xlsx'))
    except ExceptionType:
      self.fail()

  def test_correct_matrix_without_labels(self):
    """A correctly formed matrix should validate without raising an exception.
    """
    try:
      validate_worksheet(self.load_worksheet('test_data/correct_matrix_without_labels.xlsx'))
    except ExceptionType:
      self.fail()

  def test_incorrect_matrix_non_square(self):
    """A non-square matrix should raise an exception.
    """
    with self.assertRaises(AssertionError):
      validate_worksheet(self.load_worksheet('test_data/incorrect_matrix_non_square.xlsx'))

  def test_incorrect_matrix_non_symmetrical(self):
    """A non-symmeteric matrix should raise an exception.
    """
    with self.assertRaises(AssertionError):
      validate_worksheet(self.load_worksheet('test_data/incorrect_matrix_non_symmetrical.xlsx'))

  def load_worksheet(path):
    """Retrieve worksheets for testing. 
    """
    workbook = openpyxl.load_workbook(path, data_only=True)
    return workbook.active

if __name__ == '__main__':    
  unittest.main()
  
