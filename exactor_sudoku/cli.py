"""
Interactive Terminal CLI for Exactor Sudoku & Benchmark Runner.
"""

import argparse
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from exactor_sudoku.core.grid import SudokuGrid, Difficulty
from exactor_sudoku.agents.exactor_agent import ExactorSudokuAgent
from exactor_sudoku.benchmark.runner import SudokuBenchmarkRunner
from exactor_sudoku.benchmark.reporter import SudokuBenchmarkReporter


def print_cli_grid(grid: SudokuGrid):
    print("\n   1 2 3   4 5 6   7 8 9")
    print(" +-------+-------+-------+")
    for r in range(9):
        row_str = []
        for c in range(9):
            val = grid.get_cell(r, c)
            row_str.append(str(val) if val != 0 else ".")
            if c in (2, 5):
                row_str.append("|")
        print(f"{r+1}| {' '.join(row_str[:3])} | {' '.join(row_str[4:7])} | {' '.join(row_str[8:])} |")
        if r in (2, 5):
            print(" +-------+-------+-------+")
    print(" +-------+-------+-------+\n")


def play_cli():
    print("=========================================================")
    print("   EXACTOR SUDOKU: Interactive Terminal Game")
    print("=========================================================")
    grid = SudokuGrid.get_sample_puzzle(Difficulty.MEDIUM)
    print_cli_grid(grid)

    while not grid.is_complete():
        cmd = input("Enter move ('r c val' e.g. '1 2 5', 'ai' for Exactor deduction, 'q' to quit): ").strip()
        if not cmd:
            continue
        if cmd.lower() == 'q':
            break
        elif cmd.lower() == 'ai':
            agent = ExactorSudokuAgent()
            act = agent.select_action(grid)
            if act:
                grid.set_cell(act.row, act.col, act.value)
                print(f"🤖 Exactor Deduction: Placed {act.value} at ({act.row+1}, {act.col+1}) | Latency: {act.metadata.get('latency_ms', 0):.4f} ms")
                print(f"   Reasoning: {act.explanation}")
                print_cli_grid(grid)
            else:
                print("No deduction found.")
        else:
            parts = cmd.split()
            if len(parts) == 3:
                try:
                    r, c, val = int(parts[0]) - 1, int(parts[1]) - 1, int(parts[2])
                    grid.set_cell(r, c, val)
                    print_cli_grid(grid)
                except ValueError:
                    print("Invalid input.")
            else:
                print("Format: '<row> <col> <digit>'")

    if grid.is_complete():
        print("🎉 PUZZLE COMPLETED SUCCESSFULLY!")


def main():
    parser = argparse.ArgumentParser(description="Exactor Sudoku CLI & Benchmark Tool")
    parser.add_argument("--benchmark", action="store_true", help="Run automated comparative benchmark")
    parser.add_argument("--puzzles", type=int, default=15, help="Number of test puzzles")
    parser.add_argument("--difficulty", type=str, default="medium", choices=["easy", "medium", "hard", "evil"])
    parser.add_argument("--export-md", type=str, default="benchmark_report.md", help="Export Markdown report path")
    parser.add_argument("--export-json", type=str, default="benchmark_results.json", help="Export JSON path")
    parser.add_argument("--play", action="store_true", help="Start interactive CLI game")

    args = parser.parse_args()

    if args.benchmark or not args.play:
        diff = Difficulty(args.difficulty)
        print(f"\n🚀 Running Sudoku Benchmark ({args.puzzles} puzzles, difficulty: {args.difficulty.upper()})...\n")
        runner = SudokuBenchmarkRunner(difficulty=diff)
        result = runner.run_benchmark(num_puzzles=args.puzzles)

        SudokuBenchmarkReporter.print_terminal_summary(result)
        SudokuBenchmarkReporter.export_json(result, file_path=args.export_json)

        md_content = SudokuBenchmarkReporter.to_markdown(result)
        with open(args.export_md, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"📄 Markdown report saved to: {args.export_md}")
        print(f"📊 JSON results saved to: {args.export_json}\n")
    else:
        play_cli()


if __name__ == "__main__":
    main()
