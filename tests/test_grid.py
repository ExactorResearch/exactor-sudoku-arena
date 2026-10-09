"""
Unit tests for SudokuGrid.
"""

import pytest
from exactor_sudoku.core.grid import SudokuGrid, Difficulty, SAMPLE_PUZZLES


def test_grid_initialization():
    puzzle_str = SAMPLE_PUZZLES[Difficulty.EASY][0]
    grid = SudokuGrid(puzzle_str)
    assert grid.get_cell(0, 0) == 5
    assert grid.get_cell(0, 1) == 3
    assert grid.initial_fixed[0][0] is True
    assert grid.count_empty_cells() > 0
    assert grid.count_duplicate_violations() == 0


def test_candidate_calculation():
    puzzle_str = SAMPLE_PUZZLES[Difficulty.EASY][0]
    grid = SudokuGrid(puzzle_str)
    cands = grid.get_candidates(0, 2)
    assert isinstance(cands, set)
    # Row 0 has {5, 3, 7}, col 2 has {8}, block (0, 0) has {5, 3, 6, 9, 8}
    assert 5 not in cands
    assert 3 not in cands
    assert 8 not in cands


def test_duplicate_violation_detection():
    grid = SudokuGrid()
    grid.set_cell(0, 0, 5)
    grid.set_cell(0, 8, 5)  # Duplicate in row 0
    assert grid.count_duplicate_violations() == 1
