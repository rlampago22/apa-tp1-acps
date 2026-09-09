"""
TEMPLATE PARA O ALUNO — TRABALHO PRÁTICO 1 (TP1)
Disciplina: Análise e Projetos de Algoritmos (APA) — UNIPAMPA

ALGORITMO AUTORAL: Adaptive Centripetal Pincer Sort (ACPS)
Autores: Marcus Vinicius Morini Querol Junior e Vinicius Da Silva Gonçalves

Instruções do Enunciado:
1. Implemente seu método de ordenação autoral na função `my_authorial_sort`.
2. O retorno deve ser obrigatoriamente a tupla: (lista_ordenada, total_comparacoes, total_movimentacoes).
3. Execute este arquivo diretamente para rodar a suíte de testes de corretude e o benchmark rápido.
"""

from typing import Any, List, Tuple
import unittest


def my_authorial_sort(arr: List[Any]) -> Tuple[List[Any], int, int]:
    """
    ALGORITMO AUTORAL: Adaptive Centripetal Pincer Sort (ACPS).

    Concepção Autoral:
    - Etapa 1 (Sondagem Inicial das Pontas em Omega(N)): Verificação com dois ponteiros.
      Se já estiver ordenado, encerra com N-1 comparações e 0 trocas;
      se estiver decrescente, inverte in-place em N/2 trocas;
      se for homogêneo (todos iguais), encerra imediatamente.
    - Etapa 2 (Amostragem Posicional de 5 Pontos em O(1)): Seleção rápida de dois pivôs (p1 e p2)
      nos percentis de 25% e 75% usando 5 amostras fixas (início, 25%, 50%, 75% e fim).
    - Etapa 3 (Particionamento em Três Faixas): Divide o vetor em três faixas:
      menores que p1, miolo (p1 <= x <= p2) e maiores que p2.
    - Proteção para Dados Repetidos: Se p1 == p2, o miolo inteiro é isolado
      e não sofre recursão, garantindo excelente desempenho em vetores com chaves repetidas.
    - Caso Base Híbrido: Transição para Insertion Sort quando o tamanho do subproblema <= 16.

    Complexidade:
        - Melhor Caso:  Omega(N)
        - Caso Médio:   Theta(N log N)
        - Pior Caso:    O(N^2)
        - Espaço:       O(1) auxiliar in-place (O(log N) na pilha de chamadas)
        - Estabilidade: Instável (trocas distantes para priorizar velocidade)
    """
    a = list(arr)
    n = len(a)
    if n <= 1:
        return a, 0, 0

    comps = [0]
    moves = [0]
    INSERTION_THRESHOLD = 16

    # =========================================================================
    # ETAPA 1: SONDAGEM INICIAL PELAS PONTAS (DOIS PONTEIROS)
    # Avalia em O(N) se o vetor já está ordenado ou invertido.
    # =========================================================================
    is_sorted = True
    is_reverse = True
    all_equal = True

    for i in range(n - 1):
        comps[0] += 1
        if a[i] < a[i + 1]:
            is_reverse = False
            all_equal = False
        elif a[i] > a[i + 1]:
            is_sorted = False
            all_equal = False

        if not is_sorted and not is_reverse:
            break

    # Cenário 1A: Vetor já ordenado ou elementos idênticos -> Omega(N) tempo, 0 trocas
    if is_sorted or all_equal:
        return a, comps[0], 0

    # Cenário 1B: Vetor estritamente invertido -> Omega(N) tempo, N/2 trocas centrípetas
    if is_reverse:
        l_ptr = 0
        r_ptr = n - 1
        while l_ptr < r_ptr:
            a[l_ptr], a[r_ptr] = a[r_ptr], a[l_ptr]
            moves[0] += 2
            l_ptr += 1
            r_ptr -= 1
        return a, comps[0], moves[0]

    # =========================================================================
    # FASE 2: ROTINA BASE DE INSERÇÃO ADAPTATIVA (BASE CASE)
    # =========================================================================
    def _insertion_sort(low: int, high: int) -> None:
        for i in range(low + 1, high + 1):
            key = a[i]
            moves[0] += 1
            j = i - 1
            while j >= low:
                comps[0] += 1
                if a[j] > key:
                    a[j + 1] = a[j]
                    moves[0] += 1
                    j -= 1
                else:
                    break
            a[j + 1] = key
            moves[0] += 1

    # =========================================================================
    # FASE 3: RECURSÃO CENTRÍPETA TRIPARTITE COM CONGELAMENTO DE PLATÔ
    # =========================================================================
    def _sort_recursive(low: int, high: int) -> None:
        if low >= high:
            return

        size = high - low + 1
        if size <= INSERTION_THRESHOLD:
            _insertion_sort(low, high)
            return

        # 3.1. Amostragem Quíntupla Centrípeta para Seleção de Pivôs Trimodais
        sample_indices = [
            low,
            low + size // 4,
            low + size // 2,
            low + (3 * size) // 4,
            high
        ]
        sample_vals = [a[idx] for idx in sample_indices]

        # Ordena a amostra reduzida de 5 elementos
        for i in range(1, 5):
            k = sample_vals[i]
            j = i - 1
            while j >= 0:
                comps[0] += 1
                if sample_vals[j] > k:
                    sample_vals[j + 1] = sample_vals[j]
                    j -= 1
                else:
                    break
            sample_vals[j + 1] = k

        # Detecção de homogeneidade local nos extremos da amostra
        if sample_vals[0] == sample_vals[4]:
            comps[0] += 1
            is_segment_identical = True
            for k in range(low, high + 1):
                comps[0] += 1
                if a[k] != sample_vals[0]:
                    is_segment_identical = False
                    break
            if is_segment_identical:
                return

        p1 = sample_vals[1]  # 1º quartil estimado (~25%)
        p2 = sample_vals[3]  # 3º quartil estimado (~75%)

        # 3.2. Particionamento Centrípeto Tripartite In-Place
        left = low
        curr = low
        right = high

        while curr <= right:
            comps[0] += 1
            if a[curr] < p1:
                if curr != left:
                    a[curr], a[left] = a[left], a[curr]
                    moves[0] += 2
                left += 1
                curr += 1
            else:
                comps[0] += 1
                if a[curr] > p2:
                    while curr < right:
                        comps[0] += 1
                        if a[right] > p2:
                            right -= 1
                        else:
                            break
                    if curr != right:
                        a[curr], a[right] = a[right], a[curr]
                        moves[0] += 2
                    right -= 1

                    # O elemento trazido de a[right] é garantidamente <= p2.
                    comps[0] += 1
                    if a[curr] < p1:
                        if curr != left:
                            a[curr], a[left] = a[left], a[curr]
                            moves[0] += 2
                        left += 1
                    curr += 1
                else:
                    # p1 <= a[curr] <= p2
                    curr += 1

        # Salvaguarda contra estagnação de partição
        if (right - left + 1) == size:
            _insertion_sort(low, high)
            return

        # 3.3. Recursão com Congelamento de Platô (Plateau Bypass)
        # Segmento inferior (< p1)
        _sort_recursive(low, left - 1)

        # Segmento central (somente se p1 != p2; se p1 == p2, todos são iguais e o platô é congelado)
        comps[0] += 1
        if p1 != p2:
            _sort_recursive(left, right)

        # Segmento superior (> p2)
        _sort_recursive(right + 1, high)

    # Dispara a recursão
    _sort_recursive(0, n - 1)
    return a, comps[0], moves[0]


# =============================================================================
# SUÍTE DE TESTES AUTOMÁTICA DE VALIDAÇÃO
# =============================================================================
class TestStudentAuthorialSort(unittest.TestCase):
    def assert_sorted(self, original: List, result: List):
        self.assertEqual(len(result), len(original), "Tamanho divergente!")
        self.assertEqual(sorted(original), result, "A lista não foi ordenada corretamente!")

    def test_empty(self):
        res, _, _ = my_authorial_sort([])
        self.assert_sorted([], res)

    def test_single(self):
        res, _, _ = my_authorial_sort([99])
        self.assert_sorted([99], res)

    def test_sorted(self):
        data = list(range(100))
        res, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, res)

    def test_reverse(self):
        data = list(range(100, 0, -1))
        res, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, res)

    def test_identical(self):
        data = [5] * 50
        res, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, res)

    def test_random(self):
        import random
        random.seed(42)
        data = [random.randint(-1000, 1000) for _ in range(200)]
        res, _, _ = my_authorial_sort(data)
        self.assert_sorted(data, res)


if __name__ == "__main__":
    print("[TESTS] Executando testes unitarios no seu algoritmo autoral (ACPS)...")
    unittest.main(verbosity=2)
