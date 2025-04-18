
import unittest
import numpy as np
from critical_power_models import inverse_model_numpy_masked

class TestInverseModelNumpyMasked(unittest.TestCase):
    def test_positive_floats(self):
        x = np.array([1.0, 2.0, 3.0], dtype=np.float64)
        a, b = 2.0, 1.0
        expected = np.array([2.0, 1.0, 0.66666667], dtype=np.float64)
        np.testing.assert_almost_equal(inverse_model_numpy_masked(x, a, b), expected, decimal=7)

    def test_array_with_zeros(self):
        x = np.array([0.0, 1.0, 2.0], dtype=np.float64)
        a, b = 2.0, 1.0
        expected = np.array([0.0, 2.0, 1.0], dtype=np.float64)  # Zero remains zero
        np.testing.assert_almost_equal(inverse_model_numpy_masked(x, a, b), expected, decimal=7)

    def test_empty_array(self):
        x = np.array([], dtype=np.float64)
        a, b = 2.0, 1.0
        expected = np.array([], dtype=np.float64)
        np.testing.assert_array_equal(inverse_model_numpy_masked(x, a, b), expected)

    def test_large_values(self):
        x = np.array([1e10, 1e20], dtype=np.float64)
        a, b = 2.0, 1.0
        expected = np.array([2e-10, 2e-20], dtype=np.float64)
        np.testing.assert_almost_equal(inverse_model_numpy_masked(x, a, b), expected, decimal=7)

    def test_negative_exponent(self):
        x = np.array([1.0, 2.0, 3.0], dtype=np.float64)
        a, b = 2.0, -1.0
        expected = np.array([2.0, 4.0, 6.0], dtype=np.float64)
        np.testing.assert_almost_equal(inverse_model_numpy_masked(x, a, b), expected, decimal=7)

if __name__ == "__main__":
    unittest.main()
