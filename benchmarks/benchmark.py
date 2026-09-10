"""Benchmark reproduzivel dos algoritmos de ordenacao do TP1."""

import argparse
from datetime import datetime, timezone
import gc
import json
import os
import platform
import random
import statistics
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(REPO_ROOT, "src")
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


SortFunction = Callable[[List[int]], Tuple[List[int], int, int]]
DEFAULT_SIZES = [10, 100, 1000, 10000]
DEFAULT_DISTRIBUTIONS = [
    "random",
    "sorted",
    "reverse",
    "duplicates",
    "almost_sorted",
]
QUADRATIC_ALGORITHMS = {"Bubble Sort", "Selection Sort", "Insertion Sort"}


def generate_dataset(distribution: str, n: int, generator: random.Random) -> List[int]:
    if distribution == "random":
        return [generator.randint(-10 * n, 10 * n) for _ in range(n)]
    if distribution == "sorted":
        return list(range(n))
    if distribution == "reverse":
        return list(range(n, 0, -1))
    if distribution == "duplicates":
        return [generator.choice([1, 2, 3, 4, 5]) for _ in range(n)]
    if distribution == "almost_sorted":
        data = list(range(n))
        for _ in range(max(1, n // 20)):
            i = generator.randrange(n)
            j = generator.randrange(n)
            data[i], data[j] = data[j], data[i]
        return data
    raise ValueError(f"Distribuicao desconhecida: {distribution}")


def _summary(values: List[float]) -> Dict[str, float]:
    return {
        "mean": round(statistics.fmean(values), 6),
        "median": round(statistics.median(values), 6),
        "stdev": round(statistics.stdev(values), 6) if len(values) > 1 else 0.0,
        "min": round(min(values), 6),
        "max": round(max(values), 6),
    }


def _trial_seed(base_seed: int, distribution_index: int, n: int, trial: int) -> int:
    return base_seed + distribution_index * 10_000_000 + n * 101 + trial


def run_benchmark(
    algorithms: Dict[str, SortFunction],
    sizes: List[int],
    distributions: List[str],
    trials: int = 5,
    base_seed: int = 42,
    max_quadratic_n: int = 1000,
) -> Dict[str, Any]:
    """Executa cada algoritmo sobre exatamente os mesmos dados por repeticao."""
    for name, algorithm in algorithms.items():
        warmup = generate_dataset("random", 256, random.Random(base_seed))
        result, _, _ = algorithm(warmup)
        if result != sorted(warmup):
            raise AssertionError(f"Falha no aquecimento de {name}")

    results: Dict[str, Dict[str, Dict[str, Optional[Dict[str, Any]]]]] = {
        distribution: {name: {} for name in algorithms}
        for distribution in distributions
    }
    executed_runs = 0
    skipped_runs = 0

    for distribution_index, distribution in enumerate(distributions):
        print(f"[BENCHMARK] Cenario {distribution}")
        for n in sizes:
            active = [
                name
                for name in algorithms
                if not (name in QUADRATIC_ALGORITHMS and n > max_quadratic_n)
            ]
            for name in algorithms:
                if name not in active:
                    results[distribution][name][str(n)] = None
                    skipped_runs += trials

            samples: Dict[str, List[Dict[str, Any]]] = {name: [] for name in active}
            for trial in range(trials):
                seed = _trial_seed(base_seed, distribution_index, n, trial)
                data = generate_dataset(distribution, n, random.Random(seed))
                expected = sorted(data)
                order = list(active)
                random.Random(seed ^ 0xAC5).shuffle(order)

                for name in order:
                    algorithm = algorithms[name]
                    gc_was_enabled = gc.isenabled()
                    gc.disable()
                    try:
                        start = time.perf_counter_ns()
                        result, comparisons, movements = algorithm(data)
                        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
                    finally:
                        if gc_was_enabled:
                            gc.enable()

                    if result != expected:
                        raise AssertionError(
                            f"Ordenacao incorreta: {name}, {distribution}, N={n}, seed={seed}"
                        )
                    if comparisons < 0 or movements < 0:
                        raise AssertionError(f"Metricas negativas em {name}")

                    samples[name].append(
                        {
                            "seed": seed,
                            "time_ms": round(elapsed_ms, 6),
                            "comparisons": comparisons,
                            "movements": movements,
                        }
                    )
                    executed_runs += 1

            for name, trials_data in samples.items():
                times = [sample["time_ms"] for sample in trials_data]
                comparisons = [sample["comparisons"] for sample in trials_data]
                movements = [sample["movements"] for sample in trials_data]
                results[distribution][name][str(n)] = {
                    "time_ms": _summary(times),
                    "comparisons": _summary(comparisons),
                    "movements": _summary(movements),
                    "trials": trials_data,
                }

    return {
        "schema_version": 2,
        "metadata": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "operating_system": platform.platform(),
            "processor": platform.processor() or "nao informado pelo sistema",
            "machine": platform.machine(),
            "matplotlib_version": matplotlib.__version__,
            "base_seed": base_seed,
            "trials": trials,
            "sizes": sizes,
            "distributions": distributions,
            "max_quadratic_n": max_quadratic_n,
            "timing_clock": "time.perf_counter_ns",
            "garbage_collector_during_timing": "disabled",
            "dataset_policy": "same input for every algorithm in each trial",
            "executed_runs": executed_runs,
            "skipped_runs": skipped_runs,
        },
        "results": results,
    }


COLORS = {
    "Bubble Sort": "#d73027",
    "Selection Sort": "#f46d43",
    "Insertion Sort": "#fdae61",
    "Merge Sort": "#1a9850",
    "Quick Sort": "#4575b4",
    "DPES (Referencia)": "#762a83",
    "ACPS (Autoral)": "#111111",
}


def _plot_metric(
    axis: Any,
    scenario_data: Dict[str, Dict[str, Optional[Dict[str, Any]]]],
    metric: str,
    title: str,
    with_error_bars: bool = False,
) -> None:
    for name, size_map in scenario_data.items():
        points = [
            (int(n), value)
            for n, value in size_map.items()
            if value is not None
        ]
        points.sort(key=lambda point: point[0])
        x_values = [point[0] for point in points]
        y_values = [point[1][metric]["mean"] for point in points]
        style = {
            "color": COLORS.get(name),
            "marker": "o",
            "linewidth": 2.8 if name == "ACPS (Autoral)" else 1.4,
            "label": name,
        }
        if with_error_bars:
            errors = [
                min(point[1][metric]["stdev"], point[1][metric]["mean"] * 0.9)
                for point in points
            ]
            axis.errorbar(x_values, y_values, yerr=errors, capsize=2, **style)
        else:
            axis.plot(x_values, y_values, **style)

    axis.set_title(title, fontsize=11, fontweight="bold")
    axis.set_xlabel("Tamanho da entrada (N)")
    axis.grid(True, linestyle="--", alpha=0.35)
    axis.set_xscale("log", base=10)
    axis.legend(fontsize=7)


def plot_overview(payload: Dict[str, Any], output_path: str) -> None:
    results = payload["results"]
    scenarios = list(results)
    figure, axes = plt.subplots(len(scenarios), 3, figsize=(19, 4 * len(scenarios)))
    for row, scenario in enumerate(scenarios):
        _plot_metric(
            axes[row][0], results[scenario], "time_ms", f"Tempo - {scenario}", True
        )
        axes[row][0].set_ylabel("Tempo medio (ms)")
        axes[row][0].set_yscale("log")
        _plot_metric(
            axes[row][1], results[scenario], "comparisons", f"Comparacoes - {scenario}"
        )
        axes[row][1].set_ylabel("Comparacoes de chaves")
        axes[row][1].set_yscale("log")
        _plot_metric(
            axes[row][2], results[scenario], "movements", f"Movimentacoes - {scenario}"
        )
        axes[row][2].set_ylabel("Escritas na lista")
        axes[row][2].set_yscale("symlog", linthresh=1)
        axes[row][2].set_ylim(bottom=0)
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def plot_fast_algorithms(payload: Dict[str, Any], output_path: str) -> None:
    fast_names = {"Merge Sort", "Quick Sort", "DPES (Referencia)", "ACPS (Autoral)"}
    scenarios = ["random", "duplicates", "almost_sorted", "sorted"]
    figure, axes = plt.subplots(2, 2, figsize=(14, 9))
    for axis, scenario in zip(axes.flat, scenarios):
        scenario_data = {
            name: values
            for name, values in payload["results"][scenario].items()
            if name in fast_names
        }
        _plot_metric(axis, scenario_data, "time_ms", f"Tempo - {scenario}", True)
        axis.set_ylabel("Tempo medio (ms, escala log)")
        axis.set_yscale("log")
    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def plot_monotonic_comparisons(payload: Dict[str, Any], output_path: str) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    for axis, scenario in zip(axes, ["sorted", "reverse"]):
        _plot_metric(
            axis,
            payload["results"][scenario],
            "comparisons",
            f"Comparacoes em entrada {scenario}",
        )
        axis.set_ylabel("Comparacoes de chaves (escala log)")
        axis.set_yscale("log")
    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def write_markdown_summary(payload: Dict[str, Any], output_path: str) -> None:
    sizes = payload["metadata"]["sizes"]
    lines = [
        "# Resumo dos benchmarks",
        "",
        "Valores no formato `tempo medio em ms / comparacoes medias / movimentacoes medias`.",
        "",
    ]
    for scenario, algorithms in payload["results"].items():
        lines.extend(
            [
                f"## {scenario}",
                "",
                "| Algoritmo | " + " | ".join(f"N={n}" for n in sizes) + " |",
                "|---|" + "---:|" * len(sizes),
            ]
        )
        for name, size_map in algorithms.items():
            cells = []
            for n in sizes:
                result = size_map[str(n)]
                if result is None:
                    cells.append("nao executado")
                else:
                    cells.append(
                        f"{result['time_ms']['mean']:.4f} / "
                        f"{result['comparisons']['mean']:.0f} / "
                        f"{result['movements']['mean']:.0f}"
                    )
            lines.append("| " + name + " | " + " | ".join(cells) + " |")
        lines.append("")

    with open(output_path, "w", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(lines))


def main() -> None:
    assets_dir = os.path.join(REPO_ROOT, "assets")
    data_dir = os.path.join(REPO_ROOT, "data")
    parser = argparse.ArgumentParser(description="Benchmark reproduzivel do TP1")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--sizes",
        default=",".join(str(size) for size in DEFAULT_SIZES),
        help="Tamanhos separados por virgula",
    )
    parser.add_argument("--max-quadratic-n", type=int, default=1000)
    args = parser.parse_args()

    sizes = [int(value) for value in args.sizes.split(",")]
    algorithms: Dict[str, SortFunction] = {
        "Bubble Sort": bubble_sort,
        "Selection Sort": selection_sort,
        "Insertion Sort": insertion_sort,
        "Merge Sort": merge_sort,
        "Quick Sort": quick_sort,
        "DPES (Referencia)": dpes_sort,
        "ACPS (Autoral)": acps_sort,
    }

    payload = run_benchmark(
        algorithms,
        sizes,
        DEFAULT_DISTRIBUTIONS,
        trials=args.trials,
        base_seed=args.seed,
        max_quadratic_n=args.max_quadratic_n,
    )

    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    json_path = os.path.join(data_dir, "benchmark_data.json")
    summary_path = os.path.join(data_dir, "benchmark_summary.md")
    with open(json_path, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, ensure_ascii=False)
    write_markdown_summary(payload, summary_path)
    plot_overview(payload, os.path.join(assets_dir, "benchmark_results.png"))
    plot_fast_algorithms(payload, os.path.join(assets_dir, "benchmark_time_focus.png"))
    plot_monotonic_comparisons(
        payload, os.path.join(assets_dir, "benchmark_comps_bestcase.png")
    )

    metadata = payload["metadata"]
    print(
        f"[OK] {metadata['executed_runs']} execucoes validas; "
        f"{metadata['skipped_runs']} omitidas por limite quadratico."
    )
    print(f"[OK] Dados: {json_path}")
    print(f"[OK] Resumo: {summary_path}")


if __name__ == "__main__":
    main()
