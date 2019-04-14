import io
import unittest
from insight_matrix import CardSort, Interactions, Matrix


class TestCardSort(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cardsort = CardSort()
        self.cardsort.import_from_csv(
            io.StringIO(('A,01,sherry\n'
                         'A,01,tobacco\n'
                         'A,02,leather\n'
                         'B,01,sherry\n'
                         'B,02,tobacco\n'
                         'B,02,leather\n'
                         'C,01,sherry\n'))
        )

    def test_get_groups(self):
        self.assertEqual(
            self.cardsort.get_groups(),
            [
                set(['sherry', 'tobacco']),
                set(['leather']),
                set(['sherry']),
                set(['tobacco', 'leather']),
                set(['sherry'])
            ]
        )

    def test_get_elements(self):
        self.assertEqual(
            self.cardsort.get_elements(),
            ['leather', 'sherry', 'tobacco']
        )

    def test_get_jaccard(self):
        self.assertEqual(
            self.cardsort.get_jaccard('sherry', 'tobacco'),
            0.25
        )
        self.assertEqual(
            self.cardsort.get_jaccard('leather', 'tobacco'),
            1.0 / 3
        )
        self.assertEqual(
            self.cardsort.get_jaccard('leather', 'sherry'),
            0.0
        )


class TestInteractions(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.interactions = Interactions()
        self.interactions.import_from_csv(
            io.StringIO((',v1,v2,v3,v4,v5,v6,v7,v8,v9\n'
                         's1,2,0,1,2,0,0,1,0,0\n'
                         's2,0,1,1,1,0,0,-1,2,0\n'
                         's3,1,0,2,2,1,2,1,1,1\n'
                         's4,2,1,2,-1,1,-2,0,1,2\n'
                         's5,0,0,0,0,1,2,0,0,1\n'
                         's6,0,0,0,0,1,1,0,1,1\n'
                         ',,,,,,,,,\n'
                         ',1,2,1,3,3,2,1\n'
                         ',-2,-2,-2,-2,-2,-2,-4\n'
                         ',2,2,2,2,2,2,4\n'))
        )

        self.interactions2 = Interactions()
        self.interactions2.import_from_csv(
            io.StringIO((',v1,v2,v3,v4,v5,v6,v7\n'
                         'a,-2,0,1,2,0,1,1\n'
                         'b,2,0,-2,-1,2,0,1\n'
                         ',,,,,,,,,\n'
                         ',1,2,1,3,3,2,1\n'
                         ',-2,-2,-2,-2,-2,-2,-4\n'
                         ',2,2,2,2,2,2,4\n'))
        )

    def test_symmetrical_mappings(self):
        """mappings should be symmetrical: e.g., for every ('a_pos', 'b_neg') there
        should be an ('a_neg', 'p_pos').
        """
        failed_labels = []
        for label, mapping in self.interactions.mappings.items():
            if label[0] == '+':
                continue
            for n in mapping['n']:
                sym_a = 'a_{}'.format(n[1][2:])
                sym_b = 'b_{}'.format(n[0][2:])
                if (sym_a, sym_b) not in mapping['n']:
                    failed_labels.append(label)
            for d in mapping['d']:
                sym_a = 'a_{}'.format(d[1][2:])
                sym_b = 'b_{}'.format(d[0][2:])
                if (sym_a, sym_b) not in mapping['d']:
                    failed_labels.append(label)
        self.assertFalse(failed_labels, msg=', '.join(failed_labels))

    def test_no_n_d_overlap(self):
        """Be sure there is no overlap between each mapping's numerator and
        denominator.
        """
        failed_labels = []
        for label, mapping in self.interactions.mappings.items():
            if mapping['n'].intersection(mapping['d']):
                failed_labels.append(label)
        self.assertFalse(failed_labels, msg=', '.join(failed_labels))

    def test_data_loading(self):
        self.assertEqual(
            self.interactions.variable_labels,
            ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9']
        )
        self.assertEqual(
            self.interactions.element_labels,
            ['s1', 's2', 's3', 's4', 's5', 's6']
        )
        self.assertEqual(
            self.interactions.weights,
            [1, 2, 1, 3, 3, 2, 1]
        )
        self.assertEqual(
            self.interactions.neg_min,
            [-2, -2, -2, -2, -2, -2, -4]
        )
        self.assertEqual(
            self.interactions.pos_max,
            [2, 2, 2, 2, 2, 2, 4]
        )

    def test_var_int(self):
        self.assertEqual(
            self.interactions.var_int(-2, 2, a_neg=True, b_pos=True),
            1.0
        )
        self.assertEqual(
            self.interactions.var_int(-2, 2, a_pos=True, b_pos=True),
            0.0
        )
        self.assertEqual(
            self.interactions.var_int(0, 0, a_pos=True, b_pos=True),
            0.0
        )
        self.assertEqual(
            self.interactions.var_int(1, -2, a_pos=True, b_neg=True),
            0.75
        )
        self.assertEqual(
            self.interactions.var_int(2, -1, a_pos=True, b_neg=True),
            0.75
        )
        self.assertEqual(
            self.interactions.var_int(0, 2, a_nil=True, b_pos=True),
            1.0
        )
        self.assertEqual(
            self.interactions.var_int(1, 0, a_pos=True, b_nil=True),
            0.5
        )
        self.assertEqual(
            self.interactions.var_int(
                1, 1, neg_min=-4, pos_max=4, a_pos=True, b_pos=True),
            0.25
        )

        # assuming negative tests should return similar results as positive tests.
        self.assertEqual(
            self.interactions.var_int(0, 0, a_neg=True, b_neg=True),
            0.0
        )
        self.assertEqual(
            self.interactions.var_int(0, -2, a_nil=True, b_neg=True),
            1.0
        )
        self.assertEqual(
            self.interactions.var_int(-1, 0, a_neg=True, b_nil=True),
            0.5
        )
        self.assertEqual(
            self.interactions.var_int(-1, -1, neg_min=-4,
                                      pos_max=4, a_neg=True, b_neg=True),
            0.25
        )

    def test_filtered_interaction(self):
        """Example from Structured Planning by Owens, pg. 141
        """
        self.assertAlmostEqual(
            self.interactions2.filtered_interaction(0, 1),
            0.425,
            places=3
        )
        self.assertAlmostEqual(
            self.interactions2.filtered_interaction(
                0,
                1,
                filter=set((('a_neg', 'b_pos'),
                            ('a_nil', 'b_pos')))
            ),
            0.542,
            places=3
        )
        self.assertAlmostEqual(
            self.interactions2.filtered_interaction(
                0,
                1,
                filter=set((('a_pos', 'b_nil'),
                            ('a_pos', 'b_neg')))
            ),
            0.250,
            places=3
        )

    def test_balance(self):
        """Example from Structured Planning by Owens, pg. 141
        """
        self.assertAlmostEqual(
            self.interactions2.balance(0, 1),
            1.0 / 7,
            places=3
        )

    def test_interaction(self):
        """Example from Structured Planning by Owens, pg. 141
        """
        self.assertAlmostEqual(
            self.interactions2.interaction(0, 1),
            0.418,
            places=3
        )


class TestMatrix(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.symmetric_matrix = Matrix()
        self.symmetric_matrix.import_from_csv(
            io.StringIO((',apples,oranges,lemons\n'
                         'apples,1.0,0.5,0.0\n'
                         'oranges,0.5,1.0,0.5\n'
                         'lemons,0.0,0.5,1.0\n'))
        )

        self.nonsymmetric_matrix = Matrix()
        self.nonsymmetric_matrix.import_from_csv(
            io.StringIO((',cheap,good\n'
                         'aldi,1.0,1.0\n'
                         'trader joes,1.0,1.0\n'
                         'whole foods,0.0,1.0\n'))
        )

    def test_import_from_csv(self):
        """import should work correctly.
        """
        self.assertTrue(len(self.symmetric_matrix.x_labels) == 3)
        self.assertTrue(len(self.symmetric_matrix.y_labels) == 3)
        self.assertEqual(self.symmetric_matrix.data.shape, (3, 3))

        self.assertEqual(self.nonsymmetric_matrix.x_labels, ['cheap', 'good'])
        self.assertEqual(self.nonsymmetric_matrix.y_labels, [
                         'aldi', 'trader joes', 'whole foods'])
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
