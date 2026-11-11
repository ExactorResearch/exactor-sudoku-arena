# Exactor Sudoku Arena

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#license)
[![Powered by](https://img.shields.io/badge/Engine-Exactor%20Accelerator-orange.svg)](https://github.com/ExactorResearch/exactor-accelerator)
[![Latency](https://img.shields.io/badge/Fast--Path-~2ms-brightgreen.svg)](#benchmarks)
[![Solve Rate](https://img.shields.io/badge/Solve%20Rate-100%25%20(medium)-brightgreen.svg)](#benchmarks)
[![Live Demo](https://img.shields.io/badge/Demo-Interactive%20App-purple.svg)](https://sudoku.exactor.ai)

**Exactor Sudoku Arena** is an interactive demonstration and empirical evaluation platform showcasing **Exactor Accelerator** on NP-complete Constraint Satisfaction Problems (CSP).

It isolates the core failure mode of generative AI in discrete logic: **deterministic constraint propagation runs locally in sub-millisecond time with zero API cost, while genuinely underdetermined states can be escalated to a cloud oracle (TypeSafe Jev).**

---

## 🌐 Live Interactive Demo

Test the live interactive constraint solver in your browser:  
👉 **[Launch Sudoku Arena Live](https://sudoku.exactor.ai)**

* Experience the real-time split-screen duel: **Exactor SAT Invariant vs. Pure JEV (LLM/RLCD)**.
* Compare Exactor's deterministic constraint propagation against live LLM spatial reasoning.
* Inspect the dual output on every move: **Cell Placement + Axiomatic SAT Invariant Proof**.

> **Honest note on the "Pure JEV" baseline:** the agent sends each decision to the live TypeSafe Jev API when `JEV_API_KEY` is configured and *uses the returned choice*. Without a key it falls back to a *clearly labeled* local simulation (`simulated_llm: true` in move metadata) — simulated numbers are not real LLM measurements.

---

## The Challenge with AI in Constraint Satisfaction (CSP)

Sudoku is governed by 27 interlocking unit rules (9 rows, 9 columns, 9 3x3 blocks). A single duplicate number invalidates the entire board.

| Dimension | 🤖 Pure JEV (Solo LLM, live API) | 📜 Classical Backtracking (DFS) | ⚡ Exactor Accelerator (Neuro-Symbolic SAT) |
| :--- | :---: | :---: | :---: |
| **Deduction Latency** | `647.39 ms` | `23.22 ms` | **`2.09 ms` (local)** |
| **Puzzle Solve Rate** | `0.0%` (15 medium puzzles) | `100.0%` | **`100.0%`** |
| **Constraint Violations / Puzzle** | `23.5 errors` | `0.0 errors` | **`0.0 errors`** |
| **API Cost per 100 Solves** | **55 calls/puzzle — per-call billing** | $0.00 | **$0.00 (Zero API calls)** |
| **Solve Replicability** | Stochastic / Non-deterministic | Deterministic | **Deterministic on the SAT fast-path** |
| **Explainability** | Opaque natural text | None (Brute force search) | **Exact Single/Subset Invariant Proof** |

*Measured live against `api.typesafe.ai` (`JEV_API_KEY` required): 15 medium puzzles per agent, identical initial grids. Note DFS also solves 100% — Exactor's edge over classical search here is ~11x lower latency plus a formal proof per placement, not solve rate. Without a key, the Jev agent falls back to a labeled simulation (`simulated_llm: true`); simulated runs are not real LLM measurements.*

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
 │    - Evaluates Naked Singles & Hidden Singles locally │
 └───────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
 [ Logic-Solved Cells (local) ]       [ Extreme Underdetermined Puzzle (Evil) ]
        │                                 │
        ▼                                 ▼
 [ Instant Placement + Proof ]     [ Minimum Remaining Values (MRV) Oracle ]
 (~2 ms)                                │
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
  "latency_ms": 1.84,
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

# Optional: live Jev oracle for the "Pure JEV" baseline
export JEV_API_KEY="your-typesafe-key"

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

# Fast-Path step evaluation (~2 ms)
step = solver.deduce_next_move(board)
print(f"Cell: {step.cell} | Digit: {step.digit} | Proof: {step.causal_proof}")
```

---

## 📅 Enterprise Evaluation & Demo Scheduling

Explore how Exactor Accelerator solves combinatorial, rule-heavy, or constraint-satisfaction problems at sub-millisecond latency:

- **Schedule a 15-Min Architecture Review:** [Book Directly on Cal.com](https://cal.com/exactor-tech)
- **Submit Workload Requirements:** [Open Tally / Typeform Assessment](https://tally.so/r/w2xD4P)
- **Direct Commercial Inquiries:** [`contact@exactor.tech`](mailto:contact@exactor.tech)

---

## License

Dual-licensed under [MIT](LICENSE).

