"""
Classical Backtracking & Random Baseline Agents for Sudoku.
"""

import time
import random
from typing import Optional
from exactor_sudoku.agents.base import BaseSudokuAgent, SudokuAgentAction
from exactor_sudoku.core.grid import SudokuGrid


class BacktrackingSudokuAgent(BaseSudokuAgent):
    """Classical brute-force depth-first backtracking search baseline."""

    def __init__(self, name: str = "Classical Backtracking (DFS)"):
        super().__init__(name=name)

    def select_action(self, grid: SudokuGrid) -> Optional[SudokuAgentAction]:
        t0 = time.perf_counter()
        self.total_moves += 1

        all_cands = grid.get_all_candidates()
        if not all_cands:
            return None

        # Pick first empty cell
        for r in range(9):
            for c in range(9):
                if grid.get_cell(r, c) == 0:
                    cands = list(grid.get_candidates(r, c))
                    if cands:
                        val = cands[0]
                        lat_ms = (time.perf_counter() - t0) * 1000.0
                        self.total_latency_ms += lat_ms
                        self.total_guesses += 1
                        return SudokuAgentAction(
                            row=r,
                            col=c,
                            value=val,
                            confidence=0.5,
                            is_deterministic=False,
                            explanation=f"[Classical DFS] Placed first available candidate {val} at ({r}, {c}).",
                            metadata={"latency_ms": round(lat_ms, 4), "mode": "DFS_BACKTRACKING"},
                        )
        return None


class RandomSudokuAgent(BaseSudokuAgent):
    """Pure random digit placer baseline."""

    def __init__(self, name: str = "Random Baseline"):
        super().__init__(name=name)

    def select_action(self, grid: SudokuGrid) -> Optional[SudokuAgentAction]:
        t0 = time.perf_counter()
        self.total_moves += 1
        self.total_guesses += 1

        empty = [(r, c) for r in range(9) for c in range(9) if grid.get_cell(r, c) == 0]
        if not empty:
            return None

        r, c = random.choice(empty)
        val = random.randint(1, 9)
        lat_ms = (time.perf_counter() - t0) * 1000.0
        self.total_latency_ms += lat_ms

        return SudokuAgentAction(
            row=r,
            col=c,
            value=val,
            confidence=0.11,
            is_deterministic=False,
            explanation=f"[Random] Placed random digit {val} at ({r}, {c}).",
            metadata={"latency_ms": round(lat_ms, 4), "mode": "RANDOM"},
        )
