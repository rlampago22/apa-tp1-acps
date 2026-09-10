"""Suite de corretude, propriedades e instrumentacao do ACPS."""

import itertools
import os
import random
import sys
import unittest
from typing import Any, List

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from algorithms_baseline import (
    bubble_sort,
    dpes_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    selection_sort,
)
from authorial_acps import acps_sort


class CountedKey:
    """Chave que registra as avaliacoes relacionais feitas pelo algoritmo."""

    relational_calls = 0

    def __init__(self, key: int, original_position: int = 0):
        self.key = key
        self.original_position = original_position

    @classmethod
    def reset(cls) -> None:
        cls.relational_calls = 0

    def __lt__(self, other: "CountedKey") -> bool:
        type(self).relational_calls += 1
        return self.key < other.key

    def __gt__(self, other: "CountedKey") -> bool:
        type(self).relational_calls += 1
        return self.key > other.key

    def __ne__(self, other: "CountedKey") -> bool:
        type(self).relational_calls += 1
        return self.key != other.key

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CountedKey):
            return NotImplemented
        return (
            self.key == other.key
            and self.original_position == other.original_position
        )

    def __repr__(self) -> str:
        return f"CountedKey({self.key}, {self.original_position})"


class ComprehensiveTestSuite(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = random.Random(42)

    def assert_is_sorted(self, original: List[Any], result: List[Any]) -> None:
        self.assertEqual(len(result), len(original))
        self.assertEqual(result, sorted(original))

    def test_01_empty_array(self):
        result, comparisons, movements = acps_sort([])
        self.assertEqual(result, [])
        self.assertEqual(comparisons, 0)
        self.assertEqual(movements, 0)

    def test_02_single_element(self):
        result, comparisons, movements = acps_sort([42])
        self.assertEqual(result, [42])
        self.assertEqual(comparisons, 0)
        self.assertEqual(movements, 0)

    def test_03_two_elements_sorted(self):
        result, _, _ = acps_sort([10, 20])
        self.assertEqual(result, [10, 20])

    def test_04_two_elements_inverted(self):
        result, _, _ = acps_sort([20, 10])
        self.assertEqual(result, [10, 20])

    def test_05_already_sorted_small(self):
        data = list(range(100))
        result, comparisons, movements = acps_sort(data)
        self.assertEqual(result, data)
        self.assertEqual(comparisons, len(data) - 1)
        self.assertEqual(movements, 0)

    def test_06_already_sorted_large(self):
        data = list(range(1000))
        result, comparisons, movements = acps_sort(data)
        self.assertEqual(result, data)
        self.assertEqual(comparisons, 999)
        self.assertEqual(movements, 0)

    def test_07_reverse_small(self):
        data = list(range(100, 0, -1))
        result, comparisons, movements = acps_sort(data)
        self.assert_is_sorted(data, result)
        self.assertEqual(comparisons, 2 * (len(data) - 1))
        self.assertEqual(movements, 2 * (len(data) // 2))

    def test_08_reverse_large(self):
        data = list(range(1000, 0, -1))
        result, comparisons, movements = acps_sort(data)
        self.assert_is_sorted(data, result)
        self.assertEqual(comparisons, 1998)
        self.assertEqual(movements, 1000)

    def test_09_all_identical(self):
        data = [7] * 250
        result, comparisons, movements = acps_sort(data)
        self.assertEqual(result, data)
        self.assertEqual(comparisons, 2 * (len(data) - 1))
        self.assertEqual(movements, 0)

    def test_10_high_duplicates_few_unique(self):
        data = [self.generator.choice([0, 1, 2]) for _ in range(500)]
        result, _, _ = acps_sort(data)
        self.assert_is_sorted(data, result)

    def test_11_repeated_blocks(self):
        data = [10] * 50 + [2] * 50 + [50] * 50 + [25] * 50
        result, _, _ = acps_sort(data)
        self.assert_is_sorted(data, result)

    def test_12_almost_sorted(self):
        data = list(range(300))
        for _ in range(15):
            i = self.generator.randint(0, 299)
            j = self.generator.randint(0, 299)
            data[i], data[j] = data[j], data[i]
        result, _, _ = acps_sort(data)
        self.assert_is_sorted(data, result)

    def test_13_negative_and_positive(self):
        data = [self.generator.randint(-5000, 5000) for _ in range(300)]
        result, _, _ = acps_sort(data)
        self.assert_is_sorted(data, result)

    def test_14_floating_point(self):
        data = [self.generator.uniform(-100.0, 100.0) for _ in range(250)]
        result, _, _ = acps_sort(data)
        self.assert_is_sorted(data, result)

    def test_15_random_scaling(self):
        for n in [10, 100, 1000, 2500, 5000, 10000]:
            with self.subTest(n=n):
                data = [self.generator.randint(-10 * n, 10 * n) for _ in range(n)]
                result, comparisons, movements = acps_sort(data)
                self.assert_is_sorted(data, result)
                self.assertGreater(comparisons, 0)
                self.assertGreaterEqual(movements, 0)

    def test_16_non_increasing_with_duplicates(self):
        data = [5, 5, 4, 4, 3, 3, 2, 2, 1, 1]
        result, _, _ = acps_sort(data)
        self.assert_is_sorted(data, result)

    def test_17_binary_duplicates_avoid_quadratic_fallback(self):
        n = 4096
        data = [self.generator.randrange(2) for _ in range(n)]
        result, comparisons, _ = acps_sort(data)
        self.assert_is_sorted(data, result)
        self.assertLess(comparisons, 20 * n)

    def test_18_exhaustive_small_ternary_domain(self):
        for n in range(8):
            for values in itertools.product(range(3), repeat=n):
                result, _, _ = acps_sort(list(values))
                self.assertEqual(result, sorted(values))

    def test_19_input_is_preserved_by_public_interface(self):
        data = [3, 1, 2, 1]
        original = list(data)
        result, _, _ = acps_sort(data)
        self.assertEqual(data, original)
        self.assertEqual(result, sorted(original))
        self.assertIsNot(result, data)

    def test_20_comparison_counter_matches_relational_calls(self):
        data = [CountedKey(value) for value in range(100, 0, -1)]
        CountedKey.reset()
        _, comparisons, _ = acps_sort(data)
        self.assertEqual(comparisons, CountedKey.relational_calls)

    def test_21_algorithm_is_not_stable(self):
        values = [3, 3, 0, 2, 4, 3, 3, 2, 3, 2, 4, 1, 4, 1, 2, 1, 0, 4, 2, 4,
                  4, 1, 2, 0, 0, 2, 3, 4, 0, 2, 3, 2, 4, 1, 4, 3, 3, 4, 2, 0]
        data = [CountedKey(value, index) for index, value in enumerate(values)]
        result, _, _ = acps_sort(data)
        positions_by_key = {}
        for item in result:
            positions_by_key.setdefault(item.key, []).append(item.original_position)
        self.assertTrue(
            any(positions != sorted(positions) for positions in positions_by_key.values())
        )

    def test_22_classical_baselines_remain_correct(self):
        data = [self.generator.randint(-100, 100) for _ in range(100)]
        for algorithm in (
            bubble_sort,
            selection_sort,
            insertion_sort,
            merge_sort,
            quick_sort,
            dpes_sort,
        ):
            with self.subTest(algorithm=algorithm.__name__):
                result, _, _ = algorithm(data)
                self.assertEqual(result, sorted(data))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ComprehensiveTestSuite)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if outcome.wasSuccessful() else 1)
