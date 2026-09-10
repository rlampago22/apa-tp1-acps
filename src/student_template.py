"""Entrada compativel com o template oficial do TP1."""

from typing import Any, List, Tuple
import unittest

try:
    from .authorial_acps import acps_sort
except ImportError:  # Permite executar diretamente: python src/student_template.py
    from authorial_acps import acps_sort


def my_authorial_sort(arr: List[Any]) -> Tuple[List[Any], int, int]:
    """Executa a implementacao canonica do ACPS."""
    return acps_sort(arr)


class TestStudentAuthorialSort(unittest.TestCase):
    def assert_sorted(self, original: List[Any], result: List[Any]) -> None:
        self.assertEqual(len(result), len(original))
        self.assertEqual(sorted(original), result)

    def test_empty(self):
        result, _, _ = my_authorial_sort([])
        self.assert_sorted([], result)

    def test_single(self):
        result, _, _ = my_authorial_sort([99])
        self.assert_sorted([99], result)

    def test_sorted(self):
        data = list(range(100))
        result, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, result)

    def test_reverse(self):
        data = list(range(100, 0, -1))
        result, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, result)

    def test_identical(self):
        data = [5] * 50
        result, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, result)

    def test_random(self):
        import random

        generator = random.Random(42)
        data = [generator.randint(-1000, 1000) for _ in range(200)]
        result, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, result)


if __name__ == "__main__":
    print("[TESTS] Executando testes unitarios no ACPS...")
    unittest.main(verbosity=2)
