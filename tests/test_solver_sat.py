"""
Unit tests for ExactSudokuSATSolver.
"""

import pytest
from exactor_sudoku.core.grid import SudokuGrid, Difficulty, SAMPLE_PUZZLES
from exactor_sudoku.core.solver_sat import ExactSudokuSATSolver, DeductionType


def test_naked_single_detection():
    # Puzzle with immediate singles
    puzzle_str = SAMPLE_PUZZLES[Difficulty.EASY][0]
    grid = SudokuGrid(puzzle_str)
    deduction = ExactSudokuSATSolver.find_next_deduction(grid)
    assert deduction is not None
    assert deduction.is_deterministic
    assert 1 <= deduction.value <= 9


def test_full_puzzle_solve():
    puzzle_str = SAMPLE_PUZZLES[Difficulty.EASY][0]
    grid = SudokuGrid(puzzle_str)
    steps = 0
    while not grid.is_complete() and steps < 80:
        steps += 1
        deduction = ExactSudokuSATSolver.find_next_deduction(grid)
        if not deduction:
            break
        grid.set_cell(deduction.row, deduction.col, deduction.value)

    assert grid.is_complete()
    assert grid.count_duplicate_violations() == 0
