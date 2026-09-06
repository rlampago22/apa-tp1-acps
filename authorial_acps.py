"""
Adaptive Centripetal Pincer Sort (ACPS)
Algoritmo de Ordenação Autoral — Trabalho Prático 1 (TP1)
Disciplina: Análise e Projetos de Algoritmos (APA) — UNIPAMPA

Autores: Solução Autoral Acadêmica
Complexidade:
    - Melhor Caso:  Omega(N)
    - Caso Médio:   Theta(N log N)
    - Pior Caso:    O(N^2)
    - Espaço:       O(1) auxiliar in-place (O(log N) na pilha de chamadas)
    - Estabilidade: Instável (trocas simétricas centrípetas in-place)
"""

from typing import Any, List, Tuple


def acps_sort(arr: List[Any]) -> Tuple[List[Any], int, int]:
    """
    Executa a Ordenação por Pinça Centrípeta Adaptativa (ACPS).

    Parâmetros:
        arr (List[Any]): Lista de entrada contendo elementos comparáveis.

    Retorno:
        Tuple[List[Any], int, int]: (lista_ordenada, total_comparacoes, total_movimentacoes)
    """
    a = list(arr)
    n = len(a)
    if n <= 1:
        return a, 0, 0

    comps = [0]
    moves = [0]
    INSERTION_THRESHOLD = 16

    # =========================================================================
    # FASE 1: SONDAGEM E COLHEITA POR PINÇA (PINCER DIAGNOSTIC SCAN)
    # Avalia em O(N) se o vetor já possui monotonicidade global.
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

    # Cenário 1A: Vetor já ordenado ou todos os elementos idênticos -> Omega(N) tempo, 0 trocas
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

                    # O elemento recém-trazido de a[right] é comprovadamente <= p2.
                    # Verificamos apenas se ele é < p1.
                    comps[0] += 1
                    if a[curr] < p1:
                        if curr != left:
                            a[curr], a[left] = a[left], a[curr]
                            moves[0] += 2
                        left += 1
                    curr += 1
                else:
                    # Elemento no corredor central: p1 <= a[curr] <= p2
                    curr += 1

        # Salvaguarda contra estagnação de partição
        if (right - left + 1) == size:
            _insertion_sort(low, high)
            return

        # 3.3. Recursão com Congelamento de Platô (Plateau Bypass)
        # Segmento inferior: elementos < p1
        _sort_recursive(low, left - 1)

        # Segmento central: somente recursiona se p1 != p2 (se p1 == p2, todos são idênticos a p1)
        comps[0] += 1
        if p1 != p2:
            _sort_recursive(left, right)

        # Segmento superior: elementos > p2
        _sort_recursive(right + 1, high)

    # Dispara a recursão centrípeta
    _sort_recursive(0, n - 1)
    return a, comps[0], moves[0]
