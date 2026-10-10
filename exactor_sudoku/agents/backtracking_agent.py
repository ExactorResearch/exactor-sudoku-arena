"""
Classical Backtracking & Random Baseline Agents for Sudoku.
"""

import time
import random
from typing import Optional
from exactor_sudoku.agents.base import BaseSudokuAgent, SudokuAgentAction
from exactor_sudoku.core.grid import SudokuGrid


class BacktrackingSudokuAgent(BaseSudokuAgent):
    """Classical brute-force depth-first backtracking search baseline with exploration tracking."""

    def __init__(self, name: str = "Classical Backtracking (DFS)", max_node_evaluations: int = 25000):
        super().__init__(name=name)
        self.max_node_evaluations = max_node_evaluations

    def select_action(self, grid: SudokuGrid) -> Optional[SudokuAgentAction]:
        t0 = time.perf_counter()
        self.total_moves += 1

        all_cands = grid.get_all_candidates()
        if not all_cands:
            return None

        # Solve grid using classical DFS recursion with a safety node limit
        grid_copy = [row[:] for row in grid.grid]
        nodes_evaluated = [0]
        backtracks = [0]

        def is_valid(g, r, c, val):
            for i in range(9):
                if g[r][i] == val or g[i][c] == val:
                    return False
            br, bc = (r // 3) * 3, (c // 3) * 3
            for i in range(3):
                for j in range(3):
                    if g[br + i][bc + j] == val:
                        return False
            return True

        def dfs(g):
            nodes_evaluated[0] += 1
            if nodes_evaluated[0] > self.max_node_evaluations:
                return False

            for r in range(9):
                for c in range(9):
                    if g[r][c] == 0:
                        for val in range(1, 10):
                            if is_valid(g, r, c, val):
                                g[r][c] = val
                                if dfs(g):
                                    return True
                                g[r][c] = 0
                                backtracks[0] += 1
                        return False
            return True

        solved = dfs(grid_copy)
        lat_ms = (time.perf_counter() - t0) * 1000.0
        self.total_latency_ms += lat_ms

        if solved:
            # Pick first cell that differs
            for r in range(9):
                for c in range(9):
                    if grid.get_cell(r, c) == 0 and grid_copy[r][c] != 0:
                        val = grid_copy[r][c]
                        self.total_deterministic_moves += 1
                        return SudokuAgentAction(
                            row=r,
                            col=c,
                            value=val,
                            confidence=1.0,
                            is_deterministic=False,
                            explanation=f"[Classical DFS] Solved cell ({r+1}, {c+1})={val} after exploring {nodes_evaluated[0]:,} recursive search nodes and {backtracks[0]:,} backtracks.",
                            metadata={
                                "latency_ms": round(lat_ms, 4),
                                "nodes_evaluated": nodes_evaluated[0],
                                "backtracks": backtracks[0],
                                "mode": "DFS_BACKTRACKING",
                            },
                        )
        else:
            # Search limit exceeded or dead end
            self.total_guesses += 1
            # Fallback to first candidate with warning
            for r in range(9):
                for c in range(9):
                    if grid.get_cell(r, c) == 0:
                        cands = list(grid.get_candidates(r, c))
                        if cands:
                            val = cands[0]
                            return SudokuAgentAction(
                                row=r,
                                col=c,
                                value=val,
                                confidence=0.1,
                                is_deterministic=False,
                                explanation=f"[Classical DFS Exhausted/Stuck] Reached {nodes_evaluated[0]:,} node limit without finding solution. Placed guess {val} at ({r+1}, {c+1}).",
                                metadata={
                                    "latency_ms": round(lat_ms, 4),
                                    "nodes_evaluated": nodes_evaluated[0],
                                    "backtracks": backtracks[0],
                                    "exhausted": True,
                                },
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
