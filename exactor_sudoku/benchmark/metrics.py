"""
Metrics and Data Models for Sudoku Benchmarks.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SingleSudokuRecord:
    puzzle_id: int
    difficulty: str
    solved: bool
    total_moves: int
    deterministic_moves: int
    duplicate_violations: int
    total_latency_ms: float
    avg_latency_per_move_ms: float
    p95_latency_ms: float
    api_calls: int


@dataclass
class AgentSudokuMetrics:
    agent_name: str
    total_puzzles: int
    solved_count: int
    solve_rate_pct: float
    avg_moves_per_puzzle: float
    total_duplicate_violations: int
    avg_violations_per_puzzle: float
    avg_latency_per_move_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_time_seconds: float
    total_api_calls: int
    avg_api_calls_per_puzzle: float
    deterministic_accuracy_pct: float
    speedup_vs_baseline: float = 1.0
    puzzle_records: List[SingleSudokuRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "total_puzzles": self.total_puzzles,
            "solved_count": self.solved_count,
            "solve_rate_pct": round(self.solve_rate_pct, 2),
            "avg_moves_per_puzzle": round(self.avg_moves_per_puzzle, 2),
            "total_duplicate_violations": self.total_duplicate_violations,
            "avg_violations_per_puzzle": round(self.avg_violations_per_puzzle, 2),
            "avg_latency_per_move_ms": round(self.avg_latency_per_move_ms, 4),
            "p50_latency_ms": round(self.p50_latency_ms, 4),
            "p95_latency_ms": round(self.p95_latency_ms, 4),
            "p99_latency_ms": round(self.p99_latency_ms, 4),
            "total_time_seconds": round(self.total_time_seconds, 3),
            "total_api_calls": self.total_api_calls,
            "avg_api_calls_per_puzzle": round(self.avg_api_calls_per_puzzle, 1),
            "deterministic_accuracy_pct": round(self.deterministic_accuracy_pct, 2),
            "speedup_vs_baseline": round(self.speedup_vs_baseline, 1),
        }


@dataclass
class SudokuBenchmarkResult:
    timestamp: str
    difficulty: str
    num_puzzles: int
    metrics_by_agent: Dict[str, AgentSudokuMetrics]
    comparative_summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "num_puzzles": self.num_puzzles,
            "metrics": {name: m.to_dict() for name, m in self.metrics_by_agent.items()},
            "summary": self.comparative_summary,
        }
