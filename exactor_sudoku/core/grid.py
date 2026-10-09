"""
Sudoku Grid Data Structure, Validation, Puzzle Generation, and Serialization.
"""

import random
import copy
from enum import Enum
from typing import List, Set, Tuple, Optional, Dict, Any


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EVIL = "evil"


SAMPLE_PUZZLES = {
    Difficulty.EASY: [
        "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79",
        "...26.7.168..7..9.19...45..82.1...4...46.29...5...3.28..93...74.4..5..367.3.18...",
    ],
    Difficulty.MEDIUM: [
        "2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3",
        ".2.6.8...58...97......4....37....5..6.......4..8....13....2......19...81...3.2.5.",
    ],
    Difficulty.HARD: [
        "1..9.7..3.8.....7..5...31..24.6..7...7.5.8...3..1.42...92...8..4.....9.5..1.8..6",
        "...8.1...4...7...2.6.9.5.4.5..7.6..8...3.2...9..5.4..1.4.1.2.5.3...9...4...6.8...",
    ],
    Difficulty.EVIL: [
        "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..",
        "........1.2.9.4...37....5...6...1.89..2...6..98.5...3...5....76...3.8.9.4........",
    ]
}


class SudokuGrid:
    """Represents a standard 9x9 Sudoku Board with constraint checking."""

    def __init__(self, puzzle_str: Optional[str] = None):
        self.grid: List[List[int]] = [[0] * 9 for _ in range(9)]
        self.initial_fixed: List[List[bool]] = [[False] * 9 for _ in range(9)]
        
        if puzzle_str:
            self.load_from_string(puzzle_str)

    def load_from_string(self, puzzle_str: str) -> None:
        """Load 81-character puzzle string (digits 1-9 or '.'/'0')."""
        clean_str = "".join(c for c in puzzle_str if c in "0123456789.")
        if len(clean_str) != 81:
            raise ValueError(f"Invalid puzzle string length ({len(clean_str)} != 81)")

        for i, char in enumerate(clean_str):
            r, c = i // 9, i % 9
            val = int(char) if char in "123456789" else 0
            self.grid[r][c] = val
            self.initial_fixed[r][c] = (val != 0)

    def to_string(self) -> str:
        """Serialize grid to 81-character string."""
        return "".join(str(self.grid[r][c]) if self.grid[r][c] != 0 else "." for r in range(9) for c in range(9))

    def get_cell(self, r: int, c: int) -> int:
        return self.grid[r][c]

    def set_cell(self, r: int, c: int, val: int) -> bool:
        if not (0 <= r < 9 and 0 <= c < 9 and 0 <= val <= 9):
            return False
        self.grid[r][c] = val
        return True

    def get_row(self, r: int) -> List[int]:
        return [self.grid[r][c] for c in range(9)]

    def get_col(self, c: int) -> List[int]:
        return [self.grid[r][c] for r in range(9)]

    def get_block(self, block_r: int, block_c: int) -> List[int]:
        """Get 3x3 block containing block coordinates (0..2, 0..2)."""
        start_r = block_r * 3
        start_c = block_c * 3
        return [
            self.grid[r][c]
            for r in range(start_r, start_r + 3)
            for c in range(start_c, start_c + 3)
        ]

    def get_cell_block_coords(self, r: int, c: int) -> Tuple[int, int]:
        return r // 3, c // 3

    def get_candidates(self, r: int, c: int) -> Set[int]:
        """Calculate valid digit candidates for empty cell (r, c)."""
        if self.grid[r][c] != 0:
            return set()

        used = set()
        # Row and column
        for i in range(9):
            if self.grid[r][i] != 0:
                used.add(self.grid[r][i])
            if self.grid[i][c] != 0:
                used.add(self.grid[i][c])

        # 3x3 block
        br, bc = self.get_cell_block_coords(r, c)
        for row in range(br * 3, br * 3 + 3):
            for col in range(bc * 3, bc * 3 + 3):
                if self.grid[row][col] != 0:
                    used.add(self.grid[row][col])

        return set(range(1, 10)) - used

    def get_all_candidates(self) -> Dict[Tuple[int, int], Set[int]]:
        """Return candidates for all empty cells."""
        return {
            (r, c): self.get_candidates(r, c)
            for r in range(9)
            for c in range(9)
            if self.grid[r][c] == 0
        }

    def count_empty_cells(self) -> int:
        return sum(sum(1 for val in row if val == 0) for row in self.grid)

    def is_complete(self) -> bool:
        return self.count_empty_cells() == 0 and self.count_duplicate_violations() == 0

    def count_duplicate_violations(self) -> int:
        """Count constraint violations (duplicate digits in rows, cols, or 3x3 blocks)."""
        violations = 0

        # Check rows
        for r in range(9):
            seen = set()
            for c in range(9):
                val = self.grid[r][c]
                if val != 0:
                    if val in seen:
                        violations += 1
                    seen.add(val)

        # Check columns
        for c in range(9):
            seen = set()
            for r in range(9):
                val = self.grid[r][c]
                if val != 0:
                    if val in seen:
                        violations += 1
                    seen.add(val)

        # Check 3x3 blocks
        for br in range(3):
            for bc in range(3):
                seen = set()
                for r in range(br * 3, br * 3 + 3):
                    for c in range(bc * 3, bc * 3 + 3):
                        val = self.grid[r][c]
                        if val != 0:
                            if val in seen:
                                violations += 1
                            seen.add(val)

        return violations

    def clone(self) -> "SudokuGrid":
        return copy.deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid": [row[:] for row in self.grid],
            "initial_fixed": [row[:] for row in self.initial_fixed],
            "empty_cells": self.count_empty_cells(),
            "is_complete": self.is_complete(),
            "violations": self.count_duplicate_violations(),
            "puzzle_string": self.to_string(),
        }

    @staticmethod
    def get_sample_puzzle(difficulty: Difficulty = Difficulty.MEDIUM, seed: Optional[int] = None) -> "SudokuGrid":
        puzzles = SAMPLE_PUZZLES.get(difficulty, SAMPLE_PUZZLES[Difficulty.MEDIUM])
        rng = random.Random(seed)
        chosen_str = rng.choice(puzzles)
        return SudokuGrid(chosen_str)
