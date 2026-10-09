"""
Base Class and Data Contracts for Sudoku AI Agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from exactor_sudoku.core.grid import SudokuGrid


@dataclass
class SudokuAgentAction:
    row: int
    col: int
    value: int
    confidence: float
    is_deterministic: bool
    explanation: str
    metadata: Dict[str, Any]


class BaseSudokuAgent(ABC):
    """Abstract interface for Sudoku playing agents."""

    def __init__(self, name: str):
        self.name = name
        self.total_moves: int = 0
        self.total_deterministic_moves: int = 0
        self.total_guesses: int = 0
        self.total_latency_ms: float = 0.0
        self.api_calls_count: int = 0
        self.duplicate_violations: int = 0

    @abstractmethod
    def select_action(self, grid: SudokuGrid) -> Optional[SudokuAgentAction]:
        """Analyze current grid state and return the next recommended number placement."""
        pass

    def reset_metrics(self) -> None:
        self.total_moves = 0
        self.total_deterministic_moves = 0
        self.total_guesses = 0
        self.total_latency_ms = 0.0
        self.api_calls_count = 0
        self.duplicate_violations = 0
