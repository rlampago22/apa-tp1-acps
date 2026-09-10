"""
Adaptive Centripetal Pincer Sort (ACPS).

O ACPS e uma adaptacao estrutural autoral de tecnicas de Quick Sort com dois
pivos. Ele combina uma sondagem inicial de monotonicidade, amostragem fixa de
cinco elementos, particionamento tripartite in-place, congelamento de platos e
Insertion Sort para particoes pequenas.

Convencao de instrumentacao:
    - comparacao: cada avaliacao relacional entre duas chaves (<, >, ==, !=);
    - movimentacao: cada escrita de uma chave na lista de trabalho;
    - uma troca entre posicoes distintas equivale a duas movimentacoes.

Complexidade da implementacao:
    - melhor caso: Theta(N), para entradas nao decrescentes ou nao crescentes;
    - caso medio: Theta(N log N), sob a hipotese de permutacao aleatoria;
    - pior caso: Theta(N^2), devido a particoes deterministicamente desbalanceadas;
    - nucleo: in-place, com pilha de chamadas O(log N) pela eliminacao da maior
      chamada recursiva;
    - interface: Theta(N) de memoria total, pois preserva a entrada com list(arr);
    - estabilidade: nao estavel.
"""

from typing import Any, List, Tuple


INSERTION_THRESHOLD = 16


def acps_sort(arr: List[Any]) -> Tuple[List[Any], int, int]:
    """Ordena ``arr`` sem altera-la e retorna (resultado, comparacoes, movimentos)."""
    a = list(arr)
    n = len(a)
    if n <= 1:
        return a, 0, 0

    comparisons = [0]
    movements = [0]

    def _lt(left: Any, right: Any) -> bool:
        comparisons[0] += 1
        return left < right

    def _gt(left: Any, right: Any) -> bool:
        comparisons[0] += 1
        return left > right

    def _ne(left: Any, right: Any) -> bool:
        comparisons[0] += 1
        return left != right

    def _swap(i: int, j: int) -> None:
        if i != j:
            a[i], a[j] = a[j], a[i]
            movements[0] += 2

    # Fase 1: diagnostico global de monotonicidade por pares adjacentes.
    is_non_decreasing = True
    is_non_increasing = True
    for i in range(n - 1):
        if _lt(a[i], a[i + 1]):
            is_non_increasing = False
        elif _gt(a[i], a[i + 1]):
            is_non_decreasing = False

        if not is_non_decreasing and not is_non_increasing:
            break

    if is_non_decreasing:
        return a, comparisons[0], movements[0]

    if is_non_increasing:
        left = 0
        right = n - 1
        while left < right:
            _swap(left, right)
            left += 1
            right -= 1
        return a, comparisons[0], movements[0]

    def _insertion_sort(low: int, high: int) -> None:
        for i in range(low + 1, high + 1):
            key = a[i]
            movements[0] += 1
            j = i - 1
            while j >= low and _gt(a[j], key):
                a[j + 1] = a[j]
                movements[0] += 1
                j -= 1
            a[j + 1] = key
            movements[0] += 1

    def _sample_pivots(low: int, high: int) -> Tuple[Any, Any, Any]:
        """Retorna segundo, terceiro e quarto valores da amostra ordenada."""
        size = high - low + 1
        indices = (
            low,
            low + size // 4,
            low + size // 2,
            low + (3 * size) // 4,
            high,
        )
        sample = [a[index] for index in indices]

        for i in range(1, len(sample)):
            key = sample[i]
            j = i - 1
            while j >= 0 and _gt(sample[j], key):
                sample[j + 1] = sample[j]
                j -= 1
            sample[j + 1] = key

        return sample[1], sample[2], sample[3]

    def _dual_partition(low: int, high: int, p1: Any, p2: Any) -> Tuple[int, int]:
        """Cria as zonas < p1, p1 <= x <= p2 e > p2."""
        left = low
        current = low
        right = high

        while current <= right:
            if _lt(a[current], p1):
                _swap(current, left)
                left += 1
                current += 1
            elif _gt(a[current], p2):
                _swap(current, right)
                right -= 1
                # O valor trazido da direita ainda precisa ser classificado.
            else:
                current += 1

        return left, right

    def _single_pivot_partition(
        low: int, high: int, pivot: Any
    ) -> Tuple[int, int]:
        """Fallback ternario: cria as zonas < pivot, == pivot e > pivot."""
        left = low
        current = low
        right = high

        while current <= right:
            if _lt(a[current], pivot):
                _swap(current, left)
                left += 1
                current += 1
            elif _gt(a[current], pivot):
                _swap(current, right)
                right -= 1
            else:
                current += 1

        return left, right

    def _sort_recursive(low: int, high: int) -> None:
        # A maior particao e processada pela iteracao; somente as menores usam
        # recursao. Assim, a profundidade da pilha fica limitada a O(log N).
        while low < high:
            size = high - low + 1
            if size <= INSERTION_THRESHOLD:
                _insertion_sort(low, high)
                return

            p1, median, p2 = _sample_pivots(low, high)
            middle_low, middle_high = _dual_partition(low, high, p1, p2)
            distinct_pivots = _ne(p1, p2)

            if distinct_pivots and middle_low == low and middle_high == high:
                # Nenhum elemento ficou fora do corredor central. Uma particao
                # ternaria pela mediana congela pelo menos uma chave e garante
                # progresso, inclusive em vetores com apenas duas chaves.
                equal_low, equal_high = _single_pivot_partition(low, high, median)
                segments = [
                    (low, equal_low - 1),
                    (equal_high + 1, high),
                ]
            else:
                segments = [
                    (low, middle_low - 1),
                    (middle_high + 1, high),
                ]
                if distinct_pivots:
                    segments.append((middle_low, middle_high))

            segments = [segment for segment in segments if segment[0] < segment[1]]
            if not segments:
                return

            largest = max(segments, key=lambda segment: segment[1] - segment[0])
            for segment in segments:
                if segment != largest:
                    _sort_recursive(*segment)

            low, high = largest

    _sort_recursive(0, n - 1)
    return a, comparisons[0], movements[0]
