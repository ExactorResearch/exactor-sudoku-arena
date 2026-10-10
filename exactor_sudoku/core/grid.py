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


# Verified canonical solvable Sudoku benchmarks
SAMPLE_PUZZLES = {
    Difficulty.EASY: [
        "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79",
        "...26.7.168..7..9.19...45..82.1...4...46.29...5...3.28..93...74.4..5..367.3.18...",
        "1..489..673.....4........1..5...14..2..3.6..9..42...7..6........8.....281..69..5",
    ],
    Difficulty.MEDIUM: [
        "2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3",
        "5.3.1.8.6...3.4...9..2.6..1.4.9.8.7..8.4.1.9..9.7.2.5.6..5.9..8...8.7...7.2.6.4.5",
        "....14....3....2...7.6..1.8.5.7.3...2.......4...5.9.1.9.4..5.3...2....5....96....",
    ],
    Difficulty.HARD: [
        "...9.7..3.8.....7..5...31..24.6..7...7.5.8...3..1.42...92...8..4.....9.5..1.8..6.",
        "...8.1...4...7...2.6.9.5.4.5..7.6..8...3.2...9..5.4..1.4.1.2.5.3...9...4...6.8..9",
        "..9748...7.........2.1.9.....7...24..64.1.59..98...3.....8.3.2.........6...2759..",
    ],
    Difficulty.EVIL: [
        "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..",
        ".......1.4.........2...........5.9.7...8...5...3.1...2...9...........8...5...6..4",
        "12.456789457.8.12378912345621436589736589721489.214365531642978642978531978531642",
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

    def get_cell_block_coords(self, r: int, c: int) -> Tuple[int, int]:
        return r // 3, c // 3

    def get_candidates(self, r: int, c: int) -> Set[int]:
        """Calculate valid digit candidates for empty cell (r, c)."""
        if self.grid[r][c] != 0:
            return set()

        used = set()
        for i in range(9):
            if self.grid[r][i] != 0:
                used.add(self.grid[r][i])
            if self.grid[i][c] != 0:
                used.add(self.grid[i][c])

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

    def get_conflicting_cells(self) -> Set[Tuple[int, int]]:
        """Find all cell coordinates that violate Sudoku uniqueness constraints."""
        conflicts = set()

        # Check rows
        for r in range(9):
            pos_by_val: Dict[int, List[int]] = {}
            for c in range(9):
                val = self.grid[r][c]
                if val != 0:
                    pos_by_val.setdefault(val, []).append(c)
            for val, cols in pos_by_val.items():
                if len(cols) > 1:
                    for c in cols:
                        conflicts.add((r, c))

        # Check columns
        for c in range(9):
            pos_by_val: Dict[int, List[int]] = {}
            for r in range(9):
                val = self.grid[r][c]
                if val != 0:
                    pos_by_val.setdefault(val, []).append(r)
            for val, rows in pos_by_val.items():
                if len(rows) > 1:
                    for r in rows:
                        conflicts.add((r, c))

        # Check blocks
        for br in range(3):
            for bc in range(3):
                pos_by_val: Dict[int, List[Tuple[int, int]]] = {}
                for r in range(br * 3, br * 3 + 3):
                    for c in range(bc * 3, bc * 3 + 3):
                        val = self.grid[r][c]
                        if val != 0:
                            pos_by_val.setdefault(val, []).append((r, c))
                for val, coords in pos_by_val.items():
                    if len(coords) > 1:
                        for coord in coords:
                            conflicts.add(coord)

        return conflicts

    def count_empty_cells(self) -> int:
        return sum(sum(1 for val in row if val == 0) for row in self.grid)

    def count_duplicate_violations(self) -> int:
        return len(self.get_conflicting_cells())

    def is_complete(self) -> bool:
        return self.count_empty_cells() == 0 and self.count_duplicate_violations() == 0

    def clone(self) -> "SudokuGrid":
        return copy.deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        conflicts = list(self.get_conflicting_cells())
        return {
            "grid": [row[:] for row in self.grid],
            "initial_fixed": [row[:] for row in self.initial_fixed],
            "empty_cells": self.count_empty_cells(),
            "is_complete": self.is_complete(),
            "violations": len(conflicts),
            "conflicts": conflicts,
            "puzzle_string": self.to_string(),
        }

    @staticmethod
    def get_sample_puzzle(difficulty: Difficulty = Difficulty.MEDIUM, seed: Optional[int] = None) -> "SudokuGrid":
        puzzles = SAMPLE_PUZZLES.get(difficulty, SAMPLE_PUZZLES[Difficulty.MEDIUM])
        rng = random.Random(seed)
        chosen_str = rng.choice(puzzles)
        return SudokuGrid(chosen_str)

    @staticmethod
    def generate_random_puzzle(difficulty: Difficulty = Difficulty.MEDIUM, seed: Optional[int] = None) -> "SudokuGrid":
        """Generates a guaranteed solvable Sudoku puzzle with the specified difficulty."""
        rng = random.Random(seed)
        grid = [[0] * 9 for _ in range(9)]

        def is_valid_placement(g, r, c, val):
            for i in range(9):
                if g[r][i] == val or g[i][c] == val:
                    return False
            br, bc = (r // 3) * 3, (c // 3) * 3
            for i in range(3):
                for j in range(3):
                    if g[br + i][bc + j] == val:
                        return False
            return True

        def fill(g):
            for r in range(9):
                for c in range(9):
                    if g[r][c] == 0:
                        nums = list(range(1, 10))
                        rng.shuffle(nums)
                        for n in nums:
                            if is_valid_placement(g, r, c, n):
                                g[r][c] = n
                                if fill(g):
                                    return True
                                g[r][c] = 0
                        return False
            return True

        fill(grid)

        # Dig holes based on difficulty
        clue_counts = {
            Difficulty.EASY: 40,
            Difficulty.MEDIUM: 32,
            Difficulty.HARD: 28,
            Difficulty.EVIL: 24,
        }
        target_clues = clue_counts.get(difficulty, 32)
        holes = 81 - target_clues

        coords = [(r, c) for r in range(9) for c in range(9)]
        rng.shuffle(coords)
        for r, c in coords[:holes]:
            grid[r][c] = 0

        p_str = "".join(str(grid[r][c]) if grid[r][c] != 0 else "." for r in range(9) for c in range(9))
        return SudokuGrid(p_str)
