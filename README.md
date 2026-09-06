# Adaptive Centripetal Pincer Sort (ACPS)
### Trabalho Prático 1 (TP1) — Métodos de Ordenação Autorais
**Universidade Federal do Pampa (UNIPAMPA) — Campus Alegrete**  
**Disciplina:** Análise e Projetos de Algoritmos (APA)  
**Docente:** Prof. Dr. Marcelo Caggiani Luizelli  
**Discentes:**  
- Marcus Vinicius Morini Querol Junior (Matrícula: 2510100176)  
- Vinicius Da Silva Gonçalves (Matrícula: 2510100176)  

---

## 📌 Visão Geral do Algoritmo

O **Adaptive Centripetal Pincer Sort (ACPS)** é um algoritmo de ordenação in-place autoral concebido para superar a cegueira estrutural de métodos clássicos como o Quick Sort diante de dados pré-estruturados, garantindo complexidade de melhor caso em tempo linear $\Omega(N)$ e tempo logarítmico $\Theta(N \log N)$ no caso geral, utilizando estritamente $O(1)$ de memória auxiliar.

### Principais Inovações Arquiteturais:
1. **Sondagem Pincer em $\Omega(N)$:** Varredura rápida preliminar que converge pelas duas extremidades em $N-1$ comparações. Se o vetor estiver ordenado, encerra com 0 trocas; se estiver estritamente reverso, espelha in-place em $N/2$ trocas sem chamadas recursivas.
2. **Amostragem Quíntupla em $O(1)$:** Elimina a varredura global pesada do DPES (que gasta $2N$ comparações por nível), coletando 5 amostras posicionais fixas (`low`, $25\%$, $50\%$, $75\%$, `high`) para extrair dois pivôs balanceados.
3. **Particionamento Tripartite & Platô Bypass:** Segrega o vetor em 3 zonas (inferior $< p_1$, central $p_1 \le x \le p_2$, superior $> p_2$). Se $p_1 == p_2$, todo o miolo central é congelado e poupado de recursão, neutralizando a degeneração por chaves duplicadas.
4. **Cutoff Híbrido:** Subpartições pequenas ($N \le 16$) são estabilizadas localmente via Insertion Sort.

---

## 📊 Complexidade Assintótica

| Caso / Métrica | Complexidade | Condição / Detalhe |
| :--- | :---: | :--- |
| **Melhor Caso** | $\Omega(N)$ | Vetores ordenados, reversos ou uniformes ($N-1$ comparações). |
| **Caso Médio** | $\Theta(N \log N)$ | $T(N) = 3T(N/3) + \Theta(N)$ (Caso 2 do Teorema Mestre). |
| **Pior Caso** | $O(N^2)$ | Partição patologicamente desbalanceada. |
| **Espaço Auxiliar** | $O(1)$ | Estritamente in-place (pilha recursiva $O(\log N)$). |
| **Estabilidade** | Não Estável | Prioriza localidade temporal e trocas convergentes de longa distância. |

---

## 📂 Estrutura de Arquivos

* `student_template.py`: Implementação do ACPS no template oficial da UNIPAMPA, pronta para submissão e benchmarks.
* `authorial_acps.py`: Módulo do ACPS com instrumentação completa de comparações e movimentações.
* `algorithms_baseline.py`: Implementações clássicas instrumentadas de referência (Bubble, Selection, Insertion, Merge, Quick e DPES).
* `test_suite.py`: Bateria com 16 testes unitários e de estresse da disciplina (100% de aprovação).
* `benchmark.py`: Suíte estatística automatizada com 1.050 baterias de teste (Random, Sorted, Reverse, Duplicates, Almost Sorted).
* `benchmark_data.json`: Dados estatísticos tabulados de todas as execuções.
* `benchmark_results.png`: Curvas comparativas de tempo e comparações.

---

## 🚀 Como Executar

### 1. Executar a Suíte de Testes Unitários
```bash
python test_suite.py
```

### 2. Executar os Benchmarks Comparativos
```bash
python benchmark.py
```

---

## ⚖️ Declaração de Uso de IA

Em conformidade com as diretrizes do TP1 da UNIPAMPA, declaramos o uso do **Google Antigravity / Gemini 3.8 Flash** como assistente técnico de programação em par (pair-programming) para acelerar a instrumentação estatística em Matplotlib e formatação matemática. Toda a concepção algorítmica, desenho da pinça centrípeta, prova indutiva e análise assintótica pertencem integralmente à dupla discente.
