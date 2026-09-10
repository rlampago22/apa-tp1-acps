# Adaptive Centripetal Pincer Sort

Trabalho Prático 1 de Análise e Projeto de Algoritmos da Universidade Federal do Pampa, Campus Alegrete.

Autores:

- Marcus Vinicius Morini Querol Junior
- Vinicius Da Silva Goncalves

## Entregaveis

- [`RELATORIO_TECNICO_TP1.md`](RELATORIO_TECNICO_TP1.md): relatório técnico completo e editavel.
- [`output/pdf/relatorio_tecnico_acps.pdf`](output/pdf/relatorio_tecnico_acps.pdf): versao final em PDF.
- [`src/authorial_acps.py`](src/authorial_acps.py): implementação canonica do ACPS.
- [`src/student_template.py`](src/student_template.py): entrada compativel com o template da disciplina.
- [`tests/test_suite.py`](tests/test_suite.py): 22 testes de corretude, propriedades e instrumentação.
- [`benchmarks/benchmark.py`](benchmarks/benchmark.py): experimento reproduzivel.
- [`data/benchmark_data.json`](data/benchmark_data.json): repetições individuais e estatísticas agregadas.
- [`data/benchmark_summary.md`](data/benchmark_summary.md): resumo tabular dos resultados.

## Ideia do algoritmo

O ACPS e apresentado como uma adaptação estrutural autoral de Quick Sort com dois pivôs, e não como uma técnica sem antecedentes. O método combina:

1. sondagem linear de monotonicidade para reconhecer entradas não decrescentes e não crescentes;
2. amostragem de cinco posições e escolha do segundo e quarto valores da amostra ordenada como limiares;
3. particionamento centripeto em três zonas: menor, corredor central e maior;
4. congelamento do corredor quando os limiares coincidem;
5. fallback ternário pela mediana quando o particionamento dual não reduz o problema;
6. Insertion Sort somente para segmentos com no máximo 16 elementos;
7. processamento iterativo da maior partição para limitar a pilha a `O(log N)`.

## Complexidade

| Propriedade | ACPS |
|---|---|
| Melhor caso | `Theta(N)` |
| Caso médio | `Theta(N log N)` sob permutação aleatória |
| Pior caso | `Theta(N^2)` |
| Espaco do núcleo | `O(log N)` de pilha; particionamento in-place |
| Espaco total da interface | `Theta(N)`, pois a entrada e copiada |
| Estável | Nao |
| Preserva a entrada | Sim |

## Resultados principais

O benchmark final realizou 625 execuções medidas, com cinco repetições para cada combinação valida. Todos os algoritmos receberam a mesma entrada em cada repetição e toda saída foi comparada a `sorted(data)`.

Para `N=10.000`:

| Cenário | ACPS tempo médio | Comparacoes | Movimentacoes |
|---|---:|---:|---:|
| Aleatório | 119,748 ms | 156.558 | 133.011 |
| Ordenado | 4,597 ms | 9.999 | 0 |
| Reverso | 4,977 ms | 19.998 | 10.000 |
| Cinco chaves repetidas | 9,942 ms | 55.573 | 20.793 |
| Quase ordenado | 28,322 ms | 154.893 | 112.687 |

Tempos dependem da máquina e do estado do sistema. O JSON registra versoes, ambiente, sementes, repetições e desvio padrão.

## Execucao

Requer Python 3.10 ou superior.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/student_template.py
python benchmarks/benchmark.py
```

Para regenerar o PDF, tambem sao necessarios `reportlab`, `pypdf` e `pdfplumber`:

```bash
python scripts/build_report_pdf.py
```

## Convencao das métricas

- Uma comparação corresponde a cada avaliação relacional entre duas chaves: `<`, `>`, `==` ou `!=`.
- Uma movimentação corresponde a uma escrita de chave na lista de trabalho.
- Uma troca entre duas posições distintas conta como duas movimentações.
- Copias de entrada e variaveis auxiliares não entram na contagem de movimentações, seguindo a mesma convencao dos algoritmos de referência.

## Uso de inteligência artificial

O historico do trabalho utilizou Google Antigravity com Gemini e OpenAI Codex. A declaração completa, incluindo finalidade, modificacoes e validação, esta no relatório técnico. A concepcao, a revisão crítica e a defesa oral permanecem sob responsabilidade dos autores.
