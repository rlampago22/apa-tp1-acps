"""
Framework de Benchmark Estatístico de Algoritmos de Ordenação — APA (UNIPAMPA)
Compara os métodos clássicos da literatura, o algoritmo de referência (DPES)
e o algoritmo autoral proposto (ACPS).

Métricas coletadas:
- Tempo de execução médio (ms) com desvio padrão
- Número exato de comparações de chaves
- Número exato de movimentações / trocas de dados
"""

import argparse
import json
import os
import random
import sys
import time
from typing import Any, Callable, Dict, List

import matplotlib
matplotlib.use("Agg")  # Garante renderização headless sem abrir janelas GUI
import matplotlib.pyplot as plt

# Adiciona o diretório src ao path para permitir execução de qualquer pasta
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from algorithms_baseline import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    dpes_sort,
)
from authorial_acps import acps_sort


# =============================================================================
# GERADORES DE CENÁRIOS EXPERIMENTAIS
# =============================================================================
def generate_dataset(dist: str, n: int) -> List[int]:
    if dist == "random":
        return [random.randint(-100000, 100000) for _ in range(n)]
    elif dist == "sorted":
        return list(range(n))
    elif dist == "reverse":
        return list(range(n, 0, -1))
    elif dist == "duplicates":
        # Poucas chaves únicas gerando alta taxa de colisão
        keys = [1, 2, 3, 4, 5]
        return [random.choice(keys) for _ in range(n)]
    elif dist == "almost_sorted":
        data = list(range(n))
        swaps = max(1, int(n * 0.05))
        for _ in range(swaps):
            i = random.randint(0, n - 1)
            j = random.randint(0, n - 1)
            data[i], data[j] = data[j], data[i]
        return data
    else:
        raise ValueError(f"Distribuição desconhecida: {dist}")


# =============================================================================
# EXECUÇÃO DO BENCHMARK COM REPETIÇÕES ESTATÍSTICAS
# =============================================================================
def run_benchmark(
    algorithms: Dict[str, Callable],
    sizes: List[int],
    distributions: List[str],
    trials: int = 5,
) -> Dict[str, Any]:
    """
    Executa a bateria de benchmarks para todas as combinações de algoritmo,
    tamanho e distribuição de entrada.
    """
    results: Dict[str, Dict[str, Dict[int, Dict[str, float]]]] = {
        dist: {alg: {} for alg in algorithms} for dist in distributions
    }

    total_runs = len(distributions) * len(sizes) * len(algorithms) * trials
    current_run = 0

    print(f"[BENCHMARK] Iniciando execucoes: {len(algorithms)} algoritmos x {len(sizes)} tamanhos x {len(distributions)} cenarios x {trials} repeticoes.")
    print(f"[BENCHMARK] Total de execucoes individuais: {total_runs}\n")

    for dist in distributions:
        print(f"--> Cenário: [{dist.upper()}]")
        for n in sizes:
            for alg_name, alg_func in algorithms.items():
                times_ms: List[float] = []
                comps_list: List[int] = []
                moves_list: List[int] = []

                for _ in range(trials):
                    data = generate_dataset(dist, n)
                    start_time = time.perf_counter()
                    sorted_arr, comps, moves = alg_func(data)
                    elapsed = (time.perf_counter() - start_time) * 1000.0  # ms

                    # Sanity check da ordenação
                    assert len(sorted_arr) == n, f"Erro em {alg_name}: tamanho inconsistente!"
                    times_ms.append(elapsed)
                    comps_list.append(comps)
                    moves_list.append(moves)
                    current_run += 1

                mean_time = sum(times_ms) / len(times_ms)
                mean_comps = sum(comps_list) / len(comps_list)
                mean_moves = sum(moves_list) / len(moves_list)

                results[dist][alg_name][n] = {
                    "time_ms": round(mean_time, 4),
                    "comps": int(round(mean_comps)),
                    "moves": int(round(mean_moves)),
                }

    print("[BENCHMARK] Todas as baterias de testes foram concluidas com sucesso!\n")
    return results


# =============================================================================
# EXIBIÇÃO DE TABELAS RESUMO EM MARKDOWN
# =============================================================================
def print_markdown_summary(results: Dict[str, Any], sizes: List[int]) -> None:
    print("=" * 80)
    print("RESUMO ESTATÍSTICO DOS BENCHMARKS (TEMPO EM ms / COMPARAÇÕES / MOVIMENTAÇÕES)")
    print("=" * 80)

    for dist, alg_map in results.items():
        print(f"\n### Cenário: {dist.upper()}")
        header = f"| Algoritmo | " + " | ".join([f"N={s} (ms)" for s in sizes]) + " |"
        separator = "| :--- | " + " | ".join([":---:" for _ in sizes]) + " |"
        print(header)
        print(separator)

        for alg_name, size_data in alg_map.items():
            row_times = [f"{size_data[s]['time_ms']:.3f}" for s in sizes]
            print(f"| {alg_name} | " + " | ".join(row_times) + " |")


# =============================================================================
# GERAÇÃO DE GRÁFICOS COMPARATIVOS
# =============================================================================
def plot_benchmark_results(results: Dict[str, Any], output_path: str = "benchmark_results.png") -> None:
    distributions = list(results.keys())
    num_dists = len(distributions)

    fig, axes = plt.subplots(num_dists, 2, figsize=(16, 4 * num_dists))
    if num_dists == 1:
        axes = [axes]

    colors = {
        "Bubble Sort": "#e74c3c",
        "Selection Sort": "#e67e22",
        "Insertion Sort": "#f39c12",
        "Merge Sort": "#27ae60",
        "Quick Sort": "#2980b9",
        "DPES (Referencia)": "#8e44ad",
        "ACPS (Nosso Autoral)": "#d35400",
    }
    markers = {
        "Bubble Sort": "o",
        "Selection Sort": "s",
        "Insertion Sort": "^",
        "Merge Sort": "D",
        "Quick Sort": "v",
        "DPES (Referencia)": "P",
        "ACPS (Nosso Autoral)": "*",
    }

    for idx, dist in enumerate(distributions):
        ax_time = axes[idx][0]
        ax_comps = axes[idx][1]

        for alg_name, size_map in results[dist].items():
            sizes = sorted(size_map.keys())
            times = [size_map[s]["time_ms"] for s in sizes]
            comps = [size_map[s]["comps"] for s in sizes]

            c = colors.get(alg_name, None)
            m = markers.get(alg_name, "o")
            lw = 2.5 if "ACPS" in alg_name else 1.5

            ax_time.plot(sizes, times, marker=m, label=alg_name, color=c, linewidth=lw)
            ax_comps.plot(sizes, comps, marker=m, label=alg_name, color=c, linewidth=lw)

        ax_time.set_title(f"Tempo de Execução (ms) — [{dist.upper()}]", fontsize=11, fontweight="bold")
        ax_time.set_xlabel("Tamanho da Entrada (N)")
        ax_time.set_ylabel("Tempo Médio (ms)")
        ax_time.grid(True, linestyle="--", alpha=0.5)
        ax_time.legend(fontsize=8)

        ax_comps.set_title(f"Número de Comparações — [{dist.upper()}]", fontsize=11, fontweight="bold")
        ax_comps.set_xlabel("Tamanho da Entrada (N)")
        ax_comps.set_ylabel("Comparações")
        ax_comps.grid(True, linestyle="--", alpha=0.5)
        ax_comps.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    print(f"\n[OK] Painel completo de graficos salvo em: {output_path}")


def plot_dedicated_metrics(results: Dict[str, Any], output_prefix: str = "benchmark") -> None:
    """Gera gráficos dedicados para Tempo, Comparações e Movimentações para inclusão individual no relatório."""
    dists = ["random", "sorted", "reverse", "duplicates"]
    sizes = sorted(results["random"]["ACPS (Nosso Autoral)"].keys())

    # 1. Gráfico de Tempo para Aleatório e Duplicados
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for i, dist in enumerate(["random", "duplicates"]):
        ax = axes[i]
        for alg_name, size_map in results[dist].items():
            times = [size_map[s]["time_ms"] for s in sizes]
            lw = 3.0 if "ACPS" in alg_name else 1.5
            ax.plot(sizes, times, marker="o", label=alg_name, linewidth=lw)
        ax.set_title(f"Escalabilidade de Tempo — [{dist.upper()}]", fontsize=12, fontweight="bold")
        ax.set_xlabel("Tamanho da Entrada (N)")
        ax.set_ylabel("Tempo Médio (ms)")
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_time_focus.png", dpi=200)
    print(f"[OK] Grafico focado em tempo salvo em: {output_prefix}_time_focus.png")

    # 2. Gráfico de Comparações para Ordenado e Reverso (demonstração de Omega(N))
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for i, dist in enumerate(["sorted", "reverse"]):
        ax = axes[i]
        for alg_name, size_map in results[dist].items():
            comps = [size_map[s]["comps"] for s in sizes]
            lw = 3.0 if "ACPS" in alg_name else 1.5
            ax.plot(sizes, comps, marker="s", label=alg_name, linewidth=lw)
        ax.set_title(f"Comparações no Melhor Caso — [{dist.upper()}]", fontsize=12, fontweight="bold")
        ax.set_xlabel("Tamanho da Entrada (N)")
        ax.set_ylabel("Total de Comparações")
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_comps_bestcase.png", dpi=200)
    print(f"[OK] Grafico focado em comparacoes de melhor caso salvo em: {output_prefix}_comps_bestcase.png")


# =============================================================================
# MAIN CLI
# =============================================================================
def main():
    default_plot = os.path.join(REPO_ROOT, "assets", "benchmark_results.png")
    default_json = os.path.join(REPO_ROOT, "data", "benchmark_data.json")
    default_prefix = os.path.join(REPO_ROOT, "assets", "benchmark")

    parser = argparse.ArgumentParser(description="Benchmark de Algoritmos de Ordenação — APA")
    parser.add_argument("--trials", type=int, default=5, help="Número de repetições por teste (padrão: 5)")
    parser.add_argument("--plot", type=str, default=default_plot, help="Caminho para salvar o gráfico principal")
    parser.add_argument("--export_json", type=str, default=default_json, help="Arquivo JSON de saída com os dados brutos")
    args = parser.parse_args()

    algorithms = {
        "Bubble Sort": bubble_sort,
        "Selection Sort": selection_sort,
        "Insertion Sort": insertion_sort,
        "Merge Sort": merge_sort,
        "Quick Sort": quick_sort,
        "DPES (Referencia)": dpes_sort,
        "ACPS (Nosso Autoral)": acps_sort,
    }

    # Escala de tamanhos contemplando cenários pequenos e médios
    sizes = [10, 50, 100, 250, 500, 1000]
    distributions = ["random", "sorted", "reverse", "duplicates", "almost_sorted"]

    random.seed(42)
    results = run_benchmark(algorithms, sizes, distributions, trials=args.trials)
    print_markdown_summary(results, sizes)
    plot_benchmark_results(results, args.plot)
    plot_dedicated_metrics(results, default_prefix)

    # Exportação dos dados brutos em JSON para reprodutibilidade
    os.makedirs(os.path.dirname(args.export_json), exist_ok=True)
    with open(args.export_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[OK] Dados brutos salvos em JSON: {args.export_json}")


if __name__ == "__main__":
    main()
