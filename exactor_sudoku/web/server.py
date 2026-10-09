"""
FastAPI Server for Interactive Sudoku Arena & Real-Time AI Duel Visualizer.
"""

import os
import time
import random
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from exactor_sudoku.core.grid import SudokuGrid, Difficulty
from exactor_sudoku.agents.exactor_agent import ExactorSudokuAgent
from exactor_sudoku.agents.jev_pure_agent import JevPureSudokuAgent
from exactor_sudoku.agents.backtracking_agent import BacktrackingSudokuAgent
from exactor_sudoku.benchmark.runner import SudokuBenchmarkRunner

app = FastAPI(title="Exactor Sudoku AI Arena", version="1.0.0")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

sessions: Dict[str, Dict[str, Any]] = {}
agents_pool = {
    "exactor": ExactorSudokuAgent(),
    "jev": JevPureSudokuAgent(),
    "backtrack": BacktrackingSudokuAgent(),
}


class NewGameRequest(BaseModel):
    session_id: str = "default"
    difficulty: str = "medium"
    puzzle_str: Optional[str] = None
    seed: Optional[int] = None


class UserSetCellRequest(BaseModel):
    session_id: str = "default"
    row: int
    col: int
    value: int


class AIStepRequest(BaseModel):
    session_id: str = "default"
    agent_type: str = "exactor"


class DuelStepRequest(BaseModel):
    session_id: str = "default"


class BenchmarkRequest(BaseModel):
    num_puzzles: int = 15
    difficulty: str = "medium"


@app.get("/")
async def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Exactor Sudoku Arena Running</h1>")


@app.post("/api/sudoku/new")
async def new_sudoku(req: NewGameRequest):
    diff = Difficulty(req.difficulty.lower()) if req.difficulty.lower() in [d.value for d in Difficulty] else Difficulty.MEDIUM
    
    if req.puzzle_str and len(req.puzzle_str) == 81:
        grid_main = SudokuGrid(req.puzzle_str)
    else:
        grid_main = SudokuGrid.get_sample_puzzle(difficulty=diff, seed=req.seed)

    grid_exactor = grid_main.clone()
    grid_jev = grid_main.clone()

    sessions[req.session_id] = {
        "grid_main": grid_main,
        "grid_exactor": grid_exactor,
        "grid_jev": grid_jev,
        "difficulty": diff.value,
        "duel_stats": {
            "exactor": {"moves": 0, "latency_ms": 0.0, "complete": False, "violations": 0, "api_calls": 0},
            "jev": {"moves": 0, "latency_ms": 0.0, "complete": False, "violations": 0, "api_calls": 0},
        }
    }

    return {
        "status": "CREATED",
        "session_id": req.session_id,
        "grid": grid_main.to_dict(),
        "candidates": grid_main.get_all_candidates(),
        "duel_grids": {
            "exactor": grid_exactor.to_dict(),
            "jev": grid_jev.to_dict(),
        }
    }


@app.post("/api/sudoku/set-cell")
async def set_cell(req: UserSetCellRequest):
    sess = sessions.get(req.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    grid: SudokuGrid = sess["grid_main"]
    if grid.initial_fixed[req.row][req.col]:
        raise HTTPException(status_code=400, detail="Cannot edit fixed clue cell")

    grid.set_cell(req.row, req.col, req.value)
    return {
        "status": "OK",
        "grid": grid.to_dict(),
        "candidates": grid.get_all_candidates(),
    }


@app.post("/api/sudoku/ai-step")
async def ai_step(req: AIStepRequest):
    sess = sessions.get(req.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    grid: SudokuGrid = sess["grid_main"]
    if grid.is_complete():
        return {"status": "COMPLETE", "grid": grid.to_dict()}

    agent = agents_pool.get(req.agent_type.lower(), agents_pool["exactor"])
    action = agent.select_action(grid)

    if not action:
        return {"status": "NO_ACTION", "grid": grid.to_dict()}

    grid.set_cell(action.row, action.col, action.value)

    return {
        "status": "OK",
        "action": {
            "row": action.row,
            "col": action.col,
            "value": action.value,
            "confidence": action.confidence,
            "is_deterministic": action.is_deterministic,
            "explanation": action.explanation,
            "metadata": action.metadata,
        },
        "grid": grid.to_dict(),
        "candidates": grid.get_all_candidates(),
    }


@app.post("/api/sudoku/duel-step")
async def duel_step(req: DuelStepRequest):
    sess = sessions.get(req.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    g_ex: SudokuGrid = sess["grid_exactor"]
    g_jv: SudokuGrid = sess["grid_jev"]
    stats = sess["duel_stats"]

    res_exactor = None
    if not g_ex.is_complete() and g_ex.count_empty_cells() > 0:
        t0 = time.perf_counter()
        act_ex = agents_pool["exactor"].select_action(g_ex)
        lat_ex = (time.perf_counter() - t0) * 1000.0
        if act_ex:
            g_ex.set_cell(act_ex.row, act_ex.col, act_ex.value)
            stats["exactor"]["moves"] += 1
            stats["exactor"]["latency_ms"] += lat_ex
            stats["exactor"]["complete"] = g_ex.is_complete()
            stats["exactor"]["violations"] = g_ex.count_duplicate_violations()
            res_exactor = {
                "row": act_ex.row,
                "col": act_ex.col,
                "value": act_ex.value,
                "explanation": act_ex.explanation,
                "latency_ms": round(lat_ex, 4),
            }

    res_jev = None
    if not g_jv.is_complete() and g_jv.count_empty_cells() > 0:
        t0 = time.perf_counter()
        act_jv = agents_pool["jev"].select_action(g_jv)
        lat_jv = (time.perf_counter() - t0) * 1000.0
        if act_jv:
            g_jv.set_cell(act_jv.row, act_jv.col, act_jv.value)
            stats["jev"]["moves"] += 1
            stats["jev"]["latency_ms"] += lat_jv
            stats["jev"]["api_calls"] += 1
            stats["jev"]["complete"] = g_jv.is_complete()
            stats["jev"]["violations"] = g_jv.count_duplicate_violations()
            res_jev = {
                "row": act_jv.row,
                "col": act_jv.col,
                "value": act_jv.value,
                "explanation": act_jv.explanation,
                "latency_ms": round(lat_jv, 4),
            }

    return {
        "exactor": {
            "grid": g_ex.to_dict(),
            "step": res_exactor,
            "stats": stats["exactor"],
        },
        "jev": {
            "grid": g_jv.to_dict(),
            "step": res_jev,
            "stats": stats["jev"],
        },
        "is_duel_finished": g_ex.is_complete() and g_jv.is_complete(),
    }


@app.post("/api/benchmark/run")
async def run_benchmark_endpoint(req: BenchmarkRequest):
    diff = Difficulty(req.difficulty.lower()) if req.difficulty.lower() in [d.value for d in Difficulty] else Difficulty.MEDIUM
    runner = SudokuBenchmarkRunner(difficulty=diff)
    result = runner.run_benchmark(num_puzzles=req.num_puzzles)
    return result.to_dict()


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def start_server(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)
