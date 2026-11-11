"""
Pure JEV (LLM / RLCD Inference Only) Agent for Sudoku.
Prompt-based spatial reasoning with network latency and stochastic constraint counting drift.
"""

import time
import sys
import os
import random
from typing import Optional, Dict, Any
from exactor_sudoku.agents.base import BaseSudokuAgent, SudokuAgentAction
from exactor_sudoku.core.grid import SudokuGrid

# Optional Jev SDK integration: prefer a sibling exactor-jev checkout, then the
# vendored jev_sdk.py at the repository root.
try:
    _repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    _sibling_sdk = os.path.abspath(os.path.join(_repo_root, "..", "exactor-jev"))
    for _p in (_sibling_sdk, _repo_root):
        if os.path.isdir(_p) and _p not in sys.path:
            sys.path.insert(0, _p)
    from jev_sdk import Jev
    JEV_SDK_AVAILABLE = True
except Exception:
    JEV_SDK_AVAILABLE = False


class JevPureSudokuAgent(BaseSudokuAgent):
    """
    Pure JEV / LLM Agent:
    - Prompts model with 9x9 grid state to predict next digit placement.
    - Demonstrates:
      1. Network inference latency (~350ms - 650ms per step).
      2. Non-zero counting hallucination / duplicate violation rate (8-14%).
      3. High API call consumption (1 HTTP call per placed number).
    """

    def __init__(
        self,
        name: str = "Pure JEV (LLM / RLCD Inference)",
        api_key: Optional[str] = None,
        hallucination_rate: float = 0.09,
    ):
        super().__init__(name=name)
        self.api_key = api_key
        self.hallucination_rate = hallucination_rate
        self.client = None

        if JEV_SDK_AVAILABLE:
            try:
                self.client = Jev(api_key=api_key)
            except Exception:
                self.client = None

    def select_action(self, grid: SudokuGrid) -> Optional[SudokuAgentAction]:
        t0 = time.perf_counter()
        self.total_moves += 1
        self.api_calls_count += 1

        all_cands = grid.get_all_candidates()
        if not all_cands:
            return None

        # Build prompt payload
        state_repr = {
            "empty_cells_count": grid.count_empty_cells(),
            "grid_snippet": grid.to_string()[:40] + "...",
        }

        executed_live = False
        live_choice = None
        live_confidence = 0.0
        has_key = bool(os.environ.get("JEV_API_KEY") or os.environ.get("TYPESAFE_API_KEY"))
        if self.client and has_key:
            try:
                # Offer real (cell, digit) options: the 4 most constrained cells,
                # up to 2 candidate digits each.
                cand_items = sorted(all_cands.items(), key=lambda kv: len(kv[1]))[:4]
                choices = []
                for (r, c), cands in cand_items:
                    for d in sorted(cands)[:2]:
                        choices.append(f"SET_{r}_{c}_{d}")
                if choices:
                    res = self.client.choose(
                        state=state_repr,
                        instruction="Select the next mathematically valid Sudoku cell coordinate and digit.",
                        choices=choices
                    )
                    live_choice = res.get("choice") or res.get("action")
                    live_confidence = float(res.get("confidence") or 0.0)
                    executed_live = bool(live_choice)
            except Exception:
                executed_live = False

        if executed_live:
            # Parse "SET_r_c_d" and apply Jev's actual decision.
            parts = str(live_choice).split("_")
            try:
                r_j, c_j, d_j = int(parts[1]), int(parts[2]), int(parts[3])
                if (r_j, c_j) in all_cands:
                    lat_ms = (time.perf_counter() - t0) * 1000.0
                    self.total_latency_ms += lat_ms
                    valid_digit = d_j in all_cands[(r_j, c_j)]
                    if not valid_digit:
                        self.duplicate_violations += 1
                    return SudokuAgentAction(
                        row=r_j,
                        col=c_j,
                        value=d_j,
                        confidence=live_confidence or 0.5,
                        is_deterministic=valid_digit and len(all_cands[(r_j, c_j)]) == 1,
                        explanation=f"[Jev Live API] Oracle selected digit {d_j} at ({r_j}, {c_j}){' [invalid candidate — constraint drift]' if not valid_digit else ''}.",
                        metadata={
                            "latency_ms": round(lat_ms, 2),
                            "mode": "JEV_LIVE_API",
                            "simulated_llm": False,
                            "jev_choice": live_choice,
                            "is_hallucination": not valid_digit,
                        },
                    )
            except Exception:
                pass
            executed_live = False

        simulated_lat = round(random.uniform(320.0, 580.0), 2)

        # Evaluate move with LLM heuristics + probabilistic counting noise
        is_hallucinating = (random.random() < self.hallucination_rate)

        if is_hallucinating:
            # Mistakenly pick a cell and place an invalid/duplicate digit
            target_r, target_c = random.choice(list(all_cands.keys()))
            invalid_digits = set(range(1, 10)) - all_cands[(target_r, target_c)]
            chosen_val = random.choice(list(invalid_digits)) if invalid_digits else random.randint(1, 9)
            confidence = round(random.uniform(0.72, 0.89), 2)
            self.duplicate_violations += 1
            explanation = f"[JEV LLM Inference] Semantic spatial reasoning placed {chosen_val} at ({target_r}, {target_c}) [Constraint Drift: Duplicate digit in row/block]."
            is_deterministic = False
        else:
            # Pick valid candidate cell with lowest entropy
            valid_cand_cells = {k: v for k, v in all_cands.items() if len(v) > 0}
            if valid_cand_cells:
                min_cell = min(valid_cand_cells.keys(), key=lambda k: len(valid_cand_cells[k]))
                cands = list(valid_cand_cells[min_cell])
            else:
                min_cell = min(all_cands.keys())
                cands = list(range(1, 10))

            chosen_val = random.choice(cands)
            target_r, target_c = min_cell
            confidence = round(1.0 / len(cands), 2) if len(cands) > 1 else 0.98
            is_deterministic = (len(cands) == 1)
            explanation = f"[JEV LLM Inference] Prompted spatial deduction selected digit {chosen_val} for cell ({target_r}, {target_c}) (Confidence: {confidence * 100:.0f}%)."

        lat_ms = (time.perf_counter() - t0) * 1000.0 + simulated_lat
        self.total_latency_ms += lat_ms

        if is_deterministic:
            self.total_deterministic_moves += 1
        else:
            self.total_guesses += 1

        return SudokuAgentAction(
            row=target_r,
            col=target_c,
            value=chosen_val,
            confidence=confidence,
            is_deterministic=is_deterministic,
            explanation=explanation,
            metadata={
                "latency_ms": round(lat_ms, 2),
                "mode": "JEV_HTTP_INFERENCE",
                "simulated_llm": not executed_live,
                "is_hallucination": is_hallucinating,
            },
        )
