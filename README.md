# Exactor Sudoku Arena

[![License: MIT/Apache-2.0](https://img.shields.io/badge/License-MIT%2FApache--2.0-blue.svg)](#license)
[![Powered by](https://img.shields.io/badge/Engine-Exactor%20Core%20(Rust)-orange.svg)](https://github.com/ExactorResearch/exactor-accelerator)
[![Latency](https://img.shields.io/badge/Latency-0.05ms-brightgreen.svg)](#benchmarks)
[![Constraint Violations](https://img.shields.io/badge/Violations-0%20Errors-emerald.svg)](#benchmarks)
[![Live Demo](https://img.shields.io/badge/Demo-Interactive%20App-purple.svg)](https://sudoku.exactor.ai)

**Exactor Sudoku Arena** is a real-time empirical evaluation platform and interactive arena showcasing **Exactor Accelerator** on NP-complete Constraint Satisfaction Problems (CSP).

It solves the fundamental failure mode of generative AI in discrete logic: **delivering sub-millisecond deductive reasoning (< 0.05 ms) with zero hallucinations, 100% mathematical determinism, and zero marginal API cost.**

---

## 🌐 Live Interactive Demo

Test the live interactive constraint solver in your browser:  
👉 **[Launch Sudoku Arena Live](https://sudoku.exactor.ai)**

* Experience the real-time split-screen duel: **Exactor SAT Invariant vs. Pure JEV (LLM/RLCD)**.
* Compare zero constraint violations in Exactor against spatial counting drift in pure LLMs.
* Inspect the dual output on every move: **Cell Placement + Axiomatic SAT Invariant Proof**.

---

## The Challenge with AI in Constraint Satisfaction (CSP)

Sudoku is governed by 27 interlocking unit rules (9 rows, 9 columns, 9 3x3 blocks). A single duplicate number invalidates the entire board.

| Dimension | 🤖 Pure JEV (Solo LLM Cloud) | 📜 Classical Backtracking (DFS) | ⚡ Exactor Accelerator (Neuro-Symbolic SAT) |
| :--- | :---: | :---: | :---: |
| **Deduction Latency** | `~350 – 550 ms` *(High lag)* | `~0.18 ms` | **`< 0.05 ms` (Fast-Path SAT)** |
| **Constraint Violations / Puzzle** | **`29.9 errors`** *(Spatial drift)* | `0.0 errors` | **`0.0 errors` (SAT Verified)** |
| **API Cost per 100 Solves** | **$150.00 – $400.00** | $0.00 | **$0.00 (Zero API calls)** |
| **Solve Replicability** | Stochastic / Non-deterministic | Deterministic | **100% Deterministic & Provable** |
| **Explainability** | Opaque natural text | None (Brute force search) | **Exact Single/Subset Invariant Proof** |

---

## Architecture: How It Works

Exactor Sudoku Arena combines fast-path propositional SAT deduction with calibrated minimum entropy exploration:

```text
[ 9x9 Sudoku Grid State ]
           │
           ▼
 [ 1. Candidate Bitset Binarization ] ─── (Row, Column, and 3x3 Unit Constraints)
           │
           ▼
 ┌────────────────────────────────────────────────────────┐
 │ 2. Exactor Fast-Path (In-Memory SAT Deduction)         │
 │    - Evaluates Naked Singles & Hidden Singles < 0.05ms │
 └───────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
 [ Invariant Solved (95%+) ]       [ Extreme Underdetermined Puzzle (Evil) ]
        │                                 │
        ▼                                 ▼
 [ Instant Placement + Proof ]     [ Minimum Remaining Values (MRV) Oracle ]
 (0.05 ms)                                │
                                          ▼
                                   [ SQLite WAL Ledger ]
                                          │
                                          ▼
                                   [ Hot Boolean Branch Consolidation ]
```

### The Dual Output (Glass Box)
For every cell deduction, Exactor Sudoku Arena outputs both the action and the formal invariant proof:

```json
{
  "move_id": "step_42",
  "cell": [4, 7],
  "digit": 9,
  "latency_ms": 0.038,
  "execution_path": "FAST_PATH_SAT_NAKED_SINGLE",
  "causal_proof": "CandidateSet(4, 7) == {9} due to Row(4) ∪ Col(7) ∪ Box(5) covering {1..8}",
  "oracle_consulted": false
}
```

---

## Quickstart

### Prerequisites
* Python 3.9+
* pip

### Installation & Launching Local Web Arena (Port 8001)

```bash
git clone https://github.com/ExactorResearch/exactor-sudoku-arena.git
cd exactor-sudoku-arena
pip install -r requirements.txt

# Launch interactive web arena
python run_web.py
```

Once running, access the local arena at **`http://localhost:8001`**.
* 🎮 **Interactive Arena**: Play manually or trigger automated AI step-by-step solver with live sound effects.
* ⚔️ **Live Multi-Agent Duel**: Side-by-side race between Exactor and Pure JEV on identical seed puzzles.
* 📊 **Monte Carlo Benchmarks**: Measure latency, token cost, and violation metrics across Easy, Medium, Hard, and Evil grids.

---

## CLI Usage & Benchmarks

### Solve Puzzle via CLI
```bash
python run_cli.py --difficulty medium --step
```

### Run Monte Carlo Benchmark Suite
```bash
python run_benchmark.py
```

### Run Unit Tests
```bash
python -m pytest -v
```

---

## Project Structure

```text
exactor-sudoku-arena/
├── exactor_sudoku/
│   ├── solver.py            # Fast-Path SAT candidate propagation & MRV solver
│   ├── board.py             # 9x9 Grid representation & constraint checking
│   ├── web/                 # Interactive cyberpunk web arena (Port 8001)
│   └── duel.py              # Real-time multi-agent duel runner
├── run_web.py               # Launch web arena
├── run_cli.py               # Interactive CLI solver
├── run_benchmark.py         # Automated Monte Carlo benchmark runner
├── EXACTOR_METHODOLOGY.md   # Mathematical invariant specification
└── README.md
```

---

## Integration in Python

```python
from exactor_sudoku.solver import ExactorSudokuSolver

solver = ExactorSudokuSolver()
board = solver.load_puzzle("53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79")

# Fast-Path step evaluation (0.05 ms)
step = solver.deduce_next_move(board)
print(f"Cell: {step.cell} | Digit: {step.digit} | Proof: {step.causal_proof}")
```

---

## 📅 Enterprise Evaluation & Demo Scheduling

Explore how Exactor Accelerator solves combinatorial, rule-heavy, or constraint-satisfaction problems at 0.05 ms:

- **Schedule a 15-Min Architecture Review:** [Book Directly on Cal.com](https://cal.com/exactor-tech)
- **Submit Workload Requirements:** [Open Tally / Typeform Assessment](https://tally.so/r/w2xD4P)
- **Direct Commercial Inquiries:** [`contact@exactor.tech`](mailto:contact@exactor.tech)

---

## License

Dual-licensed under [MIT](LICENSE) or [Apache 2.0](LICENSE-APACHE).

