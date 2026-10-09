"""
Quick 1-Click Benchmark Runner: Exactor-Accelerator vs Pure JEV (Sudoku)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exactor-jev")))

from exactor_sudoku.cli import main

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("--benchmark")
    main()
