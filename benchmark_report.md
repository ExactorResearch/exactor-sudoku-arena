# 🔢 Benchmark Comparative Report: Exactor-Accelerator vs Pure JEV (Sudoku Arena)

- **Timestamp:** `2026-11-11T22:59:03.158054`
- **Difficulty Preset:** `MEDIUM`
- **Total Puzzles Tested:** `15` (Identical initial grid clues)

## 📊 Summary Performance Matrix

| Metric / Dimension | Pure JEV (Solo LLM/RLCD) | Exactor-Accelerator (Neuro-Symbolic SAT) | Classical Backtracking | Advantage / Delta |
| :--- | :---: | :---: | :---: | :---: |
| **Avg Latency per Deduction** | `421.51 ms` | **`1.4024 ms`** | `11.7100 ms` | **301x Faster (Sub-ms Fast Path)** |
| **Puzzle Solve Rate (%)** | `0.0%` | **`100.0%`** | `100.0%` | **+100.0% Solve Rate Lift** |
| **Duplicate Violations / Puzzle** | `21.5 errors` | **`0.0 errors`** | `0.0 errors` | SAT-verified placements vs LLM spatial drift |
| **API Calls per Puzzle** | `55.0 calls` | **`0.0 calls`** (In-Memory SAT) | `0.0 calls` | **100% Token & Cost Elimination** |
| **Deduction Replicability** | Stochastic (Temperature drift) | **100% Deterministic & Provable** | Deterministic | **Formal Mathematical Guarantee** |
| **Explainability** | Opaque text generation | **Formal Boolean Single / Subset Proof** | None (Brute force) | **Full Audit Trail** |

## 🔬 Key Architectural Insights

1. **High-Frequency Constraint Propagation**: Sudoku has 27 interlocking unit constraints (9 rows, 9 cols, 9 boxes). Exactor evaluates the candidate matrix locally (1.402 ms/deduction measured) with zero API calls, whereas the LLM baseline pays an HTTP roundtrip per cell.
2. **Constraint Drift**: LLMs can lose cross-column or block context on dense boards, creating invalid duplicate entries; Exactor's fast-path only commits SAT-verified placements.
3. **Optimal Search Guidance**: For Evil/Extreme difficulty boards where logic alone requires bifurcation branching, Exactor uses Minimum Remaining Values (MRV) guided by calibrated tie-breaking.