"""
Interactive CLI Runner for Exactor Sudoku.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exactor-jev")))

from exactor_sudoku.cli import play_cli

if __name__ == "__main__":
    play_cli()
