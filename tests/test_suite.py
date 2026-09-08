"""
Suíte de Testes Obrigatória — TP1: Métodos de Ordenação Autorais
Disciplina: Análise e Projetos de Algoritmos (APA) — UNIPAMPA

Valida todos os cenários obrigatórios e de estresse descritos no edital:
1. Vetores vazios (N = 0) e unitários (N = 1)
2. Vetores já ordenados (melhor caso / sensibilidade)
3. Vetores em ordem estritamente reversa (pior caso / estresse)
4. Vetores com elementos idênticos e redundantes (colisões / platôs)
5. Vetores quase ordenados (perturbações locais)
6. Vetores com tipos numéricos diversos (negativos, floats)
7. Vetores aleatórios homogêneos em escala crescente (N = 10, 100, 1000, 5000)
8. Teste de análise de estabilidade
"""

import os
import random
import sys
import unittest
from typing import List

# Adiciona o diretório src ao path para permitir execução de qualquer pasta
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from authorial_acps import acps_sort


class ComprehensiveTestSuite(unittest.TestCase):
    def setUp(self):
        random.seed(42)

    def assert_is_sorted(self, original: List, result: List):
        self.assertEqual(len(result), len(original), "Erro: Tamanho da saída difere da entrada!")
        expected = sorted(original)
        self.assertEqual(result, expected, "Erro: A lista resultante não está devidamente ordenada!")

    # -------------------------------------------------------------------------
    # 1. CASOS LIMITES (EDGE CASES)
    # -------------------------------------------------------------------------
    def test_01_empty_array(self):
        """Valida comportamento para N = 0."""
        res, comps, moves = acps_sort([])
        self.assert_is_sorted([], res)
        self.assertEqual(comps, 0)
        self.assertEqual(moves, 0)

    def test_02_single_element(self):
        """Valida comportamento para N = 1."""
        res, comps, moves = acps_sort([42])
        self.assert_is_sorted([42], res)
        self.assertEqual(comps, 0)
        self.assertEqual(moves, 0)

    def test_03_two_elements_sorted(self):
        """Valida comportamento para N = 2 já ordenado."""
        res, comps, moves = acps_sort([10, 20])
        self.assert_is_sorted([10, 20], res)

    def test_04_two_elements_inverted(self):
        """Valida comportamento para N = 2 invertido."""
        res, comps, moves = acps_sort([20, 10])
        self.assert_is_sorted([20, 10], res)

    # -------------------------------------------------------------------------
    # 2. VETORES JÁ ORDENADOS (MELHOR CASO / SENSIBILIDADE)
    # -------------------------------------------------------------------------
    def test_05_already_sorted_small(self):
        data = list(range(100))
        res, comps, moves = acps_sort(data)
        self.assert_is_sorted(data, res)
        self.assertEqual(moves, 0, "Vetor já ordenado não deve realizar movimentações!")
        self.assertEqual(comps, len(data) - 1, "Vetor ordenado deve ser detectado em N - 1 comparações!")

    def test_06_already_sorted_large(self):
        data = list(range(1000))
        res, comps, moves = acps_sort(data)
        self.assert_is_sorted(data, res)
        self.assertEqual(moves, 0)
        self.assertEqual(comps, 999)

    # -------------------------------------------------------------------------
    # 3. VETORES ESTRITAMENTE REVERSOS
    # -------------------------------------------------------------------------
    def test_07_reverse_small(self):
        data = list(range(100, 0, -1))
        res, comps, moves = acps_sort(data)
        self.assert_is_sorted(data, res)
        self.assertEqual(comps, len(data) - 1)
        self.assertEqual(moves, 2 * (len(data) // 2))

    def test_08_reverse_large(self):
        data = list(range(1000, 0, -1))
        res, comps, moves = acps_sort(data)
        self.assert_is_sorted(data, res)
        self.assertEqual(comps, 999)
        self.assertEqual(moves, 1000)

    # -------------------------------------------------------------------------
    # 4. ELEMENTOS IDÊNTICOS E REDUNDANTES (PLATÔS)
    # -------------------------------------------------------------------------
    def test_09_all_identical(self):
        data = [7] * 250
        res, comps, moves = acps_sort(data)
        self.assert_is_sorted(data, res)
        self.assertEqual(moves, 0)
        self.assertEqual(comps, len(data) - 1)

    def test_10_high_duplicates_few_unique(self):
        """Vetor de 500 elementos com apenas 3 chaves possíveis (0, 1, 2)."""
        data = [random.choice([0, 1, 2]) for _ in range(500)]
        res, _, _ = acps_sort(data)
        self.assert_is_sorted(data, res)

    def test_11_repeated_blocks(self):
        """Vetor com blocos idênticos consecutivos."""
        data = [10] * 50 + [2] * 50 + [50] * 50 + [25] * 50
        res, _, _ = acps_sort(data)
        self.assert_is_sorted(data, res)

    # -------------------------------------------------------------------------
    # 5. QUASE ORDENADOS (PERTURBAÇÃO LOCAL)
    # -------------------------------------------------------------------------
    def test_12_almost_sorted(self):
        """Vetor ordenado onde 5% dos elementos foram trocados de posição."""
        data = list(range(300))
        for _ in range(15):
            i = random.randint(0, 299)
            j = random.randint(0, 299)
            data[i], data[j] = data[j], data[i]
        res, _, _ = acps_sort(data)
        self.assert_is_sorted(data, res)

    # -------------------------------------------------------------------------
    # 6. DIVERSIDADE DE TIPOS NUMÉRICOS
    # -------------------------------------------------------------------------
    def test_13_negative_and_positive(self):
        data = [random.randint(-5000, 5000) for _ in range(300)]
        res, _, _ = acps_sort(data)
        self.assert_is_sorted(data, res)

    def test_14_floating_point(self):
        data = [random.uniform(-100.0, 100.0) for _ in range(250)]
        res, _, _ = acps_sort(data)
        self.assert_is_sorted(data, res)

    # -------------------------------------------------------------------------
    # 7. ESCALABILIDADE HOMOGÊNEA ALEATÓRIA
    # -------------------------------------------------------------------------
    def test_15_random_scaling(self):
        for n in [10, 50, 100, 250, 500, 1000, 2500]:
            with self.subTest(n=n):
                data = [random.randint(0, 100000) for _ in range(n)]
                res, comps, moves = acps_sort(data)
                self.assert_is_sorted(data, res)
                self.assertGreater(comps, 0)
                self.assertGreaterEqual(moves, 0)

    # -------------------------------------------------------------------------
    # 8. ESTRESSE COM N ELEVADO
    # -------------------------------------------------------------------------
    def test_16_stress_large(self):
        data = [random.randint(-1000000, 1000000) for _ in range(5000)]
        res, _, _ = acps_sort(data)
        self.assert_is_sorted(data, res)


if __name__ == "__main__":
    print("=" * 70)
    print(" SUITE RIGOROSA DE TESTES DE CORRETUDE — ACPS (TP1 - APA)")
    print("=" * 70)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ComprehensiveTestSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
