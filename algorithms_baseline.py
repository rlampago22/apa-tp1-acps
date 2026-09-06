"""
Algoritmos Clássicos de Ordenação e Algoritmo de Referência (DPES)
Disciplina: Análise e Projetos de Algoritmos (APA) - UNIPAMPA

Todos os algoritmos retornam a tupla: (lista_ordenada, total_comparacoes, total_movimentacoes).
"""

from typing import Any, List, Tuple


# =============================================================================
# 1. BUBBLE SORT (com flag de parada antecipada)
# =============================================================================
def bubble_sort(arr: List[Any]) -> Tuple[List[Any], int, int]:
    a = list(arr)
    n = len(a)
    comps = 0
    moves = 0

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comps += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                moves += 2
                swapped = True
        if not swapped:
            break

    return a, comps, moves


# =============================================================================
# 2. SELECTION SORT
# =============================================================================
def selection_sort(arr: List[Any]) -> Tuple[List[Any], int, int]:
    a = list(arr)
    n = len(a)
    comps = 0
    moves = 0

    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comps += 1
            if a[j] < a[min_idx]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            moves += 2

    return a, comps, moves


# =============================================================================
# 3. INSERTION SORT
# =============================================================================
def insertion_sort(arr: List[Any]) -> Tuple[List[Any], int, int]:
    a = list(arr)
    n = len(a)
    comps = 0
    moves = 0

    for i in range(1, n):
        key = a[i]
        moves += 1
        j = i - 1
        while j >= 0:
            comps += 1
            if a[j] > key:
                a[j + 1] = a[j]
                moves += 1
                j -= 1
            else:
                break
        a[j + 1] = key
        moves += 1

    return a, comps, moves


# =============================================================================
# 4. MERGE SORT
# =============================================================================
def merge_sort(arr: List[Any]) -> Tuple[List[Any], int, int]:
    a = list(arr)
    n = len(a)
    if n <= 1:
        return a, 0, 0

    comps = [0]
    moves = [0]

    def _merge_sort_recursive(lst: List[Any]) -> List[Any]:
        if len(lst) <= 1:
            return lst

        mid = len(lst) // 2
        left = _merge_sort_recursive(lst[:mid])
        right = _merge_sort_recursive(lst[mid:])

        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            comps[0] += 1
            if left[i] <= right[j]:
                merged.append(left[i])
                moves[0] += 1
                i += 1
            else:
                merged.append(right[j])
                moves[0] += 1
                j += 1

        while i < len(left):
            merged.append(left[i])
            moves[0] += 1
            i += 1

        while j < len(right):
            merged.append(right[j])
            moves[0] += 1
            j += 1

        return merged

    result = _merge_sort_recursive(a)
    return result, comps[0], moves[0]


# =============================================================================
# 5. QUICK SORT (Mediana de 3 com particionamento in-place de Hoare)
# =============================================================================
def quick_sort(arr: List[Any]) -> Tuple[List[Any], int, int]:
    a = list(arr)
    n = len(a)
    if n <= 1:
        return a, 0, 0

    comps = [0]
    moves = [0]

    def _quick_sort(low: int, high: int) -> None:
        if low >= high:
            return

        mid = low + (high - low) // 2
        comps[0] += 1
        if a[mid] < a[low]:
            a[low], a[mid] = a[mid], a[low]
            moves[0] += 2
        comps[0] += 1
        if a[high] < a[low]:
            a[low], a[high] = a[high], a[low]
            moves[0] += 2
        comps[0] += 1
        if a[high] < a[mid]:
            a[mid], a[high] = a[high], a[mid]
            moves[0] += 2

        pivot = a[mid]
        a[mid], a[high - 1] = a[high - 1], a[mid]
        moves[0] += 2

        i = low
        j = high - 1

        while True:
            while True:
                i += 1
                comps[0] += 1
                if a[i] >= pivot:
                    break
            while True:
                j -= 1
                comps[0] += 1
                if a[j] <= pivot:
                    break

            if i >= j:
                break

            a[i], a[j] = a[j], a[i]
            moves[0] += 2

        a[i], a[high - 1] = a[high - 1], a[i]
        moves[0] += 2

        _quick_sort(low, i - 1)
        _quick_sort(i + 1, high)

    if n <= 3:
        for i in range(1, n):
            k = a[i]
            moves[0] += 1
            j = i - 1
            while j >= 0:
                comps[0] += 1
                if a[j] > k:
                    a[j + 1] = a[j]
                    moves[0] += 1
                    j -= 1
                else:
                    break
            a[j + 1] = k
            moves[0] += 1
        return a, comps[0], moves[0]

    _quick_sort(0, n - 1)
    return a, comps[0], moves[0]


# =============================================================================
# 6. DPES SORT (Dual-Pivot Extremes Sieve Sort — Referência do Enunciado)
# =============================================================================
def dpes_sort(arr: List[Any]) -> Tuple[List[Any], int, int]:
    a = list(arr)
    n = len(a)
    if n <= 1:
        return a, 0, 0

    comps = [0]
    moves = [0]
    INSERTION_THRESHOLD = 16

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

    def _sort_recursive(low: int, high: int) -> None:
        if low >= high:
            return

        size = high - low + 1
        if size <= INSERTION_THRESHOLD:
            _insertion_sort(low, high)
            return

        min_idx = low
        max_idx = low
        for k in range(low + 1, high + 1):
            comps[0] += 1
            if a[k] < a[min_idx]:
                min_idx = k
            comps[0] += 1
            if a[k] > a[max_idx]:
                max_idx = k

        comps[0] += 1
        if a[min_idx] == a[max_idx]:
            return

        if min_idx != low:
            a[low], a[min_idx] = a[min_idx], a[low]
            moves[0] += 2
            if max_idx == low:
                max_idx = min_idx

        if max_idx != high:
            a[high], a[max_idx] = a[max_idx], a[high]
            moves[0] += 2

        min_val = a[low]
        max_val = a[high]

        try:
            span = max_val - min_val
            p1 = min_val + span / 3
            p2 = min_val + (2 * span) / 3
        except TypeError:
            mid = low + size // 2
            comps[0] += 1
            if a[low] > a[mid]:
                p1, p2 = a[mid], a[low]
            else:
                p1, p2 = a[low], a[mid]

        left = low + 1
        curr = low + 1
        right = high - 1

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

                    comps[0] += 1
                    if a[curr] < p1:
                        if curr != left:
                            a[curr], a[left] = a[left], a[curr]
                            moves[0] += 2
                        left += 1
                curr += 1

        _sort_recursive(low, left - 1)
        _sort_recursive(left, right)
        _sort_recursive(right + 1, high)

    _sort_recursive(0, n - 1)
    return a, comps[0], moves[0]
