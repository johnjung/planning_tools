import unittest

class TestModCluster(unittest.TestCase):
    def test_symmetrical_cluster():
        raise NotImplementedError
    
    def test_asymmetrical_cluster():
        raise NotImplementedError
    
    def test_reorder_rows(self):
        self.assertEqual(
            reorder_rows(
                [[1, 2, 3],
                 [4, 5, 6],
                 [7, 8, 9]],
                (0, 2, 1)
            ),
            [[1, 2, 3],
             [7, 8, 9],
             [4, 5, 6]]
        )
    
    def test_reorder_cols():
        self.assertEqual(
            reorder_cols(
                [[1, 2, 3],
                 [4, 5, 6],
                 [7, 8, 9]],
                (0, 2, 1)
            ),
            [[1, 3, 2],
             [4, 6, 5],
             [7, 9, 8]],
        )
    
    def test_is_symmetrical(self):
        self.assertFalse(
            is_symmetrical(
                [[0, 1, 0],
                 [0, 1, 0],
                 [0, 0, 1]]
            )
        )
        self.assertFalse(
            is_symmetrical(
                [[1, 0, 0, 0],
                 [0, 1, 0, 0],
                 [0, 0, 1, 0]]
            )
        )
        self.assertFalse(
            is_symmetrical(
                [[1, 0, 0],
                 [0, 1, 0],
                 [0, 0, 1],
                 [0, 0, 0]]
            )
        )
        self.assertTrue(
            is_symmetrical(
                [[1, 0, 0],
                 [0, 1, 0],
                 [0, 0, 1]]
            )
        )
    
    def test_delta_matrix(self):
        m = [[1, 3, 2, 3, 3], 
             [2, 1, 1, 3, 3],
             [3, 3, 2, 1, 2]]
        self.assertEqual(
            delta_matrix(m, True),
            [[0, 3, 3, 5, 4],
             [3, 0, 2, 3, 3],
             [3, 2, 0, 4, 3],
             [5, 3, 4, 0, 1],
             [4, 3, 3, 1, 0]]
        )
        self.assertEqual(
            delta_matrix(m, False),
            [[0, 4, 5],
             [4, 0, 7],
             [5, 7, 0]]
        )
    
    def test_cluster_arr():
        raise NotImplementedError
    
    def test_resorted_arr(self):
        raise NotImplementedError
    
    def test_remove_row_col(self):
        self.assertEqual(
            remove_row_col(
                [[1, 2, 3],
                 [4, 5, 6],
                 [7, 8, 9]],
                1
            ),
            [[1, 3],
             [7, 9]]
        )
    
    def test_new_cluster():
        raise NotImplementedError
