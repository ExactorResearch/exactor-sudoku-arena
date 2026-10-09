"""
Unit tests for ExactorSudokuAgent.
"""

import pytest
from exactor_sudoku.core.grid import SudokuGrid, Difficulty, SAMPLE_PUZZLES
from exactor_sudoku.agents.exactor_agent import ExactorSudokuAgent


def test_exactor_agent_deduction():
    agent = ExactorSudokuAgent()
    grid = SudokuGrid(SAMPLE_PUZZLES[Difficulty.MEDIUM][0])
    action = agent.select_action(grid)
    
    assert action is not None
    assert 0 <= action.row < 9
    assert 0 <= action.col < 9
    assert 1 <= action.value <= 9
    assert action.confidence >= 0.5
    assert "Fast-Path SAT" in action.explanation or "Constraint" in action.explanation


def test_benchmark_runner_execution():
    from exactor_sudoku.benchmark.runner import SudokuBenchmarkRunner
    from exactor_sudoku.agents.backtracking_agent import BacktrackingSudokuAgent
    
    agents = [ExactorSudokuAgent(), BacktrackingSudokuAgent()]
    runner = SudokuBenchmarkRunner(agents=agents, difficulty=Difficulty.EASY)
    result = runner.run_benchmark(num_puzzles=2)
    
    assert result.num_puzzles == 2
    assert "Exactor-Accelerator (Neuro-Symbolic SAT)" in result.metrics_by_agent
    exactor_m = result.metrics_by_agent["Exactor-Accelerator (Neuro-Symbolic SAT)"]
    assert exactor_m.total_puzzles == 2
    assert exactor_m.total_duplicate_violations == 0
