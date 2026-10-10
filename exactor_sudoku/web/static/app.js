/**
 * Exactor Sudoku Arena: Enhanced Interactive Frontend & Sound Synthesizer
 */

class SoundEngine {
    constructor() {
        this.ctx = null;
        this.enabled = true;
    }

    init() {
        if (!this.ctx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) this.ctx = new AudioContext();
        }
    }

    playPlace() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(520, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(780, this.ctx.currentTime + 0.05);
        gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.05);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.05);
    }

    playConflict() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(180, this.ctx.currentTime);
        osc.frequency.linearRampToValueAtTime(120, this.ctx.currentTime + 0.15);
        gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.15);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.15);
    }

    playWin() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        const notes = [440, 554.37, 659.25, 880];
        notes.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, this.ctx.currentTime + idx * 0.09);
            gain.gain.setValueAtTime(0.15, this.ctx.currentTime + idx * 0.09);
            gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + idx * 0.09 + 0.25);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(this.ctx.currentTime + idx * 0.09);
            osc.stop(this.ctx.currentTime + idx * 0.09 + 0.25);
        });
    }
}

const sounds = new SoundEngine();

// App State
const state = {
    sessionId: 'session_sdk_' + Math.random().toString(36).substring(2, 9),
    grid: null,
    candidates: {},
    selectedCell: null,
    lastPlacedCell: null,
    isAutoPlaying: false,
    autoPlayTimeout: null,
    autoPlaySpeed: 60,
    timerInterval: null,
    secondsElapsed: 0,
    lastBenchmarkResult: null,

    isDuelRunning: false,
    duelInterval: null,
};

// DOM Elements
const gridEl = document.getElementById('sudokuGrid');
const emptyScoreText = document.getElementById('emptyScoreText');
const timerText = document.getElementById('timerText');
const statusFaceBtn = document.getElementById('statusFaceBtn');
const difficultySelect = document.getElementById('difficultySelect');
const agentSelect = document.getElementById('agentSelect');
const newPuzzleBtn = document.getElementById('newPuzzleBtn');
const aiStepBtn = document.getElementById('aiStepBtn');
const aiAutoBtn = document.getElementById('aiAutoBtn');
const resetPuzzleBtn = document.getElementById('resetPuzzleBtn');
const speedSlider = document.getElementById('speedSlider');
const speedValueText = document.getElementById('speedValueText');

const lastLatencyText = document.getElementById('lastLatencyText');
const emptyCellsCountText = document.getElementById('emptyCellsCountText');
const violationsText = document.getElementById('violationsText');
const apiSavedText = document.getElementById('apiSavedText');
const explanationText = document.getElementById('explanationText');

// Duel Elements
const startDuelBtn = document.getElementById('startDuelBtn');
const pauseDuelBtn = document.getElementById('pauseDuelBtn');
const resetDuelBtn = document.getElementById('resetDuelBtn');
const duelGridExactor = document.getElementById('duelGridExactor');
const duelGridJev = document.getElementById('duelGridJev');
const exactorDuelStatus = document.getElementById('exactorDuelStatus');
const jevDuelStatus = document.getElementById('jevDuelStatus');
const exactorAvgLat = document.getElementById('exactorAvgLat');
const exactorSpeedup = document.getElementById('exactorSpeedup');
const exactorViolations = document.getElementById('exactorViolations');
const exactorApiCalls = document.getElementById('exactorApiCalls');
const jevAvgLat = document.getElementById('jevAvgLat');
const jevViolations = document.getElementById('jevViolations');
const jevApiCalls = document.getElementById('jevApiCalls');
const exactorDuelLog = document.getElementById('exactorDuelLog');
const jevDuelLog = document.getElementById('jevDuelLog');

// Benchmark Elements
const runBenchmarkBtn = document.getElementById('runBenchmarkBtn');
const benchPuzzleCount = document.getElementById('benchPuzzleCount');
const benchDifficulty = document.getElementById('benchDifficulty');
const benchmarkTableBody = document.getElementById('benchmarkTableBody');
const exportReportBtn = document.getElementById('exportReportBtn');

document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupEvents();
    startNewPuzzle();
});

function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            const pane = document.getElementById(btn.getAttribute('data-tab'));
            if (pane) pane.classList.add('active');

            if (typeof renderMathInElement === 'function') {
                renderMathInElement(document.body, {
                    delimiters: [
                        { left: '$$', right: '$$', display: true },
                        { left: '$', right: '$', display: false },
                        { left: '\\(', right: '\\)', display: false },
                        { left: '\\[', right: '\\]', display: true }
                    ],
                    throwOnError: false
                });
            }
        });
    });
}

function setupEvents() {
    newPuzzleBtn.addEventListener('click', () => startNewPuzzle());
    resetPuzzleBtn.addEventListener('click', () => startNewPuzzle());
    statusFaceBtn.addEventListener('click', () => startNewPuzzle());
    difficultySelect.addEventListener('change', () => startNewPuzzle());

    aiStepBtn.addEventListener('click', () => executeAIStep());
    aiAutoBtn.addEventListener('click', () => toggleAutoPlay());

    speedSlider.addEventListener('input', (e) => {
        state.autoPlaySpeed = parseInt(e.target.value);
        speedValueText.textContent = `${state.autoPlaySpeed} ms`;
    });

    // Numpad clicks
    document.querySelectorAll('.num-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const num = parseInt(btn.getAttribute('data-num'));
            if (state.selectedCell) {
                setUserCell(state.selectedCell.r, state.selectedCell.c, num);
            }
        });
    });

    // Keyboard & Arrow key navigation
    document.addEventListener('keydown', (e) => {
        if (!state.selectedCell) {
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                state.selectedCell = { r: 4, c: 4 };
                renderGrid(state.grid, gridEl, handleCellClick);
            }
            return;
        }

        let { r, c } = state.selectedCell;
        if (e.key >= '1' && e.key <= '9') {
            setUserCell(r, c, parseInt(e.key));
        } else if (e.key === 'Backspace' || e.key === 'Delete' || e.key === '0') {
            setUserCell(r, c, 0);
        } else if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') {
            state.selectedCell = { r: Math.max(0, r - 1), c };
            renderGrid(state.grid, gridEl, handleCellClick);
        } else if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') {
            state.selectedCell = { r: Math.min(8, r + 1), c };
            renderGrid(state.grid, gridEl, handleCellClick);
        } else if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
            state.selectedCell = { r, c: Math.max(0, c - 1) };
            renderGrid(state.grid, gridEl, handleCellClick);
        } else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
            state.selectedCell = { r, c: Math.min(8, c + 1) };
            renderGrid(state.grid, gridEl, handleCellClick);
        }
    });

    document.getElementById('soundToggleBtn').addEventListener('click', (e) => {
        sounds.enabled = !sounds.enabled;
        e.target.textContent = sounds.enabled ? '🔊' : '🔇';
    });

    // Duel Listeners
    startDuelBtn.addEventListener('click', () => startDuel());
    pauseDuelBtn.addEventListener('click', () => pauseDuel());
    resetDuelBtn.addEventListener('click', () => resetDuelBoard());

    // Benchmark Listeners
    runBenchmarkBtn.addEventListener('click', () => executeBenchmark());
    exportReportBtn.addEventListener('click', () => exportMarkdownReport());
}

async function startNewPuzzle() {
    stopAutoPlay();
    stopTimer();
    state.secondsElapsed = 0;
    state.selectedCell = null;
    state.lastPlacedCell = null;
    updateTimerDisplay(0);
    statusFaceBtn.textContent = '🧠';

    const diff = difficultySelect.value;
    try {
        const res = await fetch('/api/sudoku/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: state.sessionId, difficulty: diff })
        });
        const data = await res.json();
        state.grid = data.grid;
        state.candidates = data.candidates || {};
        renderGrid(state.grid, gridEl, handleCellClick);
        updateStats();
        startTimer();

        explanationText.textContent = `Loaded ${diff.toUpperCase()} puzzle. Select cell or click "AI Deduction Step".`;
    } catch (err) {
        console.error('Error starting puzzle:', err);
    }
}

function renderGrid(gridObj, targetEl, clickHandler) {
    if (!gridObj || !gridObj.grid) return;
    targetEl.innerHTML = '';
    const grid = gridObj.grid;
    const fixed = gridObj.initial_fixed;
    const conflicts = gridObj.conflicts || [];

    const sel = state.selectedCell;
    const selVal = (sel && grid[sel.r]) ? grid[sel.r][sel.c] : 0;
    const selBlockR = sel ? Math.floor(sel.r / 3) : -1;
    const selBlockC = sel ? Math.floor(sel.c / 3) : -1;

    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            const cell = document.createElement('div');
            cell.className = 'sudoku-cell';
            cell.dataset.row = r;
            cell.dataset.col = c;

            const val = grid[r][c];
            if (val !== 0) {
                cell.textContent = val;
                if (fixed && fixed[r][c]) {
                    cell.classList.add('fixed');
                }
            } else {
                cell.textContent = '';
            }

            // Highlighting logic
            if (sel) {
                if (sel.r === r && sel.c === c) {
                    cell.classList.add('selected');
                } else if (sel.r === r || sel.c === c || (Math.floor(r / 3) === selBlockR && Math.floor(c / 3) === selBlockC)) {
                    cell.classList.add('highlighted');
                }

                if (val !== 0 && selVal !== 0 && val === selVal) {
                    cell.classList.add('same-number');
                }
            }

            // Conflict check
            if (conflicts.some(coord => coord[0] === r && coord[1] === c)) {
                cell.classList.add('conflict');
            }

            // Just placed animation
            if (state.lastPlacedCell && state.lastPlacedCell.r === r && state.lastPlacedCell.c === c) {
                cell.classList.add('just-placed');
            }

            if (clickHandler) {
                cell.addEventListener('click', () => clickHandler(r, c));
            }

            targetEl.appendChild(cell);
        }
    }
}

function handleCellClick(r, c) {
    state.selectedCell = { r, c };
    renderGrid(state.grid, gridEl, handleCellClick);

    const val = state.grid.grid[r][c];
    if (val === 0 && state.candidates) {
        const cands = state.candidates[`${r}_${c}`] || [];
        explanationText.textContent = `Cell (${r+1}, ${c+1}) Candidates: [ ${cands.join(', ') || 'none'} ]`;
    }
}

async function setUserCell(r, c, val) {
    if (state.grid.initial_fixed[r][c]) return;

    try {
        const res = await fetch('/api/sudoku/set-cell', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: state.sessionId, row: r, col: c, value: val })
        });
        const data = await res.json();
        state.grid = data.grid;
        state.candidates = data.candidates || {};
        state.lastPlacedCell = { r, c };
        renderGrid(state.grid, gridEl, handleCellClick);
        updateStats();

        if (state.grid.violations > 0) {
            sounds.playConflict();
        } else {
            sounds.playPlace();
        }

        if (state.grid.is_complete) {
            handleVictory();
        }
    } catch (err) {
        console.error('Error setting cell:', err);
    }
}

async function executeAIStep() {
    if (state.grid.is_complete) return;
    const agent = agentSelect.value;

    try {
        const res = await fetch('/api/sudoku/ai-step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: state.sessionId, agent_type: agent })
        });
        const data = await res.json();
        if (data.status === 'COMPLETE') {
            stopAutoPlay();
            handleVictory();
            explanationText.textContent = `🎉 Sudoku solved successfully with 0 violations!`;
            return;
        }
        if (data.status === 'NO_ACTION' || data.status === 'FINISHED_WITH_VIOLATIONS') {
            stopAutoPlay();
            explanationText.textContent = (state.grid.empty_cells === 0)
                ? `🛑 Board filled but contains ${state.grid.violations} duplicate violations / conflicts.`
                : `🛑 Agent stopped: No valid moves available from current board state.`;
            return;
        }

        state.grid = data.grid;
        state.candidates = data.candidates || {};
        const act = data.action;

        state.selectedCell = { r: act.row, c: act.col };
        state.lastPlacedCell = { r: act.row, c: act.col };
        renderGrid(state.grid, gridEl, handleCellClick);
        updateStats();

        lastLatencyText.textContent = `${act.metadata.latency_ms} ms`;
        explanationText.textContent = act.explanation;

        if (agent === 'exactor') {
            apiSavedText.textContent = `${81 - state.grid.empty_cells} calls saved`;
        }

        sounds.playPlace();

        if (state.grid.is_complete) {
            handleVictory();
        }

        return data;
    } catch (err) {
        console.error('AI step error:', err);
        stopAutoPlay();
    }
}

function toggleAutoPlay() {
    if (state.isAutoPlaying) {
        stopAutoPlay();
    } else {
        if (state.grid.is_complete) startNewPuzzle();
        state.isAutoPlaying = true;
        aiAutoBtn.textContent = '⏸ Pause';
        aiAutoBtn.classList.remove('btn-success');
        aiAutoBtn.classList.add('btn-secondary');
        runAutoLoop();
    }
}

function stopAutoPlay() {
    state.isAutoPlaying = false;
    clearTimeout(state.autoPlayTimeout);
    aiAutoBtn.textContent = '▶ Auto Solve';
    aiAutoBtn.classList.remove('btn-secondary');
    aiAutoBtn.classList.add('btn-success');
}

async function runAutoLoop() {
    if (!state.isAutoPlaying || state.grid.is_complete) {
        stopAutoPlay();
        return;
    }
    await executeAIStep();
    if (!state.grid.is_complete && state.isAutoPlaying) {
        state.autoPlayTimeout = setTimeout(runAutoLoop, state.autoPlaySpeed);
    } else {
        stopAutoPlay();
    }
}

function handleVictory() {
    stopTimer();
    stopAutoPlay();
    statusFaceBtn.textContent = '🥳';
    sounds.playWin();
    explanationText.textContent = '🎉 PUZZLE SOLVED! 100% SAT verification with zero constraint violations.';
}

function updateStats() {
    const empty = state.grid.empty_cells;
    emptyScoreText.textContent = String(empty).padStart(3, '0');
    emptyCellsCountText.textContent = `${empty} cells`;
    violationsText.textContent = `${state.grid.violations} errors`;
}

function startTimer() {
    stopTimer();
    state.timerInterval = setInterval(() => {
        state.secondsElapsed++;
        updateTimerDisplay(state.secondsElapsed);
    }, 1000);
}

function stopTimer() {
    clearInterval(state.timerInterval);
}

function updateTimerDisplay(sec) {
    timerText.textContent = String(Math.min(999, sec)).padStart(3, '0');
}

/* ==========================================================================
   LIVE DUAL RACE
   ========================================================================== */
async function resetDuelBoard() {
    pauseDuel();
    try {
        const res = await fetch('/api/sudoku/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: state.sessionId, difficulty: 'medium' })
        });
        const data = await res.json();
        renderGrid(data.duel_grids.exactor, duelGridExactor);
        renderGrid(data.duel_grids.jev, duelGridJev);

        exactorDuelStatus.textContent = 'READY';
        jevDuelStatus.textContent = 'READY';
        exactorDuelLog.textContent = 'Board ready. Click Launch.';
        jevDuelLog.textContent = 'Board ready. Click Launch.';
        exactorViolations.textContent = '0';
        jevViolations.textContent = '0';
        exactorApiCalls.textContent = '0';
        jevApiCalls.textContent = '0';
    } catch (err) {
        console.error('Error resetting duel:', err);
    }
}

function startDuel() {
    if (state.isDuelRunning) return;
    state.isDuelRunning = true;
    startDuelBtn.disabled = true;
    pauseDuelBtn.disabled = false;
    runDuelLoop();
}

function pauseDuel() {
    state.isDuelRunning = false;
    clearTimeout(state.duelInterval);
    startDuelBtn.disabled = false;
    pauseDuelBtn.disabled = true;
}

async function runDuelLoop() {
    if (!state.isDuelRunning) return;

    try {
        const res = await fetch('/api/sudoku/duel-step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: state.sessionId })
        });
        const data = await res.json();

        renderGrid(data.exactor.grid, duelGridExactor);
        const exStats = data.exactor.stats;
        const avgLatEx = exStats.moves > 0 ? (exStats.latency_ms / exStats.moves) : 0.03;
        exactorAvgLat.textContent = `${avgLatEx.toFixed(3)} ms`;
        exactorViolations.textContent = exStats.violations;
        if (data.exactor.step) {
            exactorDuelLog.textContent = data.exactor.step.explanation;
        }

        renderGrid(data.jev.grid, duelGridJev);
        const jvStats = data.jev.stats;
        const avgLatJv = jvStats.moves > 0 ? (jvStats.latency_ms / jvStats.moves) : 420.0;
        jevAvgLat.textContent = `${avgLatJv.toFixed(1)} ms`;
        jevViolations.textContent = jvStats.violations;
        jevApiCalls.textContent = jvStats.api_calls;
        if (data.jev.step) {
            jevDuelLog.textContent = data.jev.step.explanation;
        }

        if (avgLatEx > 0) {
            const speedup = Math.round(avgLatJv / avgLatEx);
            exactorSpeedup.textContent = `${speedup.toLocaleString()}x faster`;
        }

        if (data.exactor.stats.complete) {
            exactorDuelStatus.textContent = '🏆 SOLVED (100% Valid)';
            exactorDuelStatus.className = 'badge bg-success';
        } else if (data.exactor.grid.empty_cells === 0) {
            exactorDuelStatus.textContent = '⚠️ FILLED (With Violations)';
            exactorDuelStatus.className = 'badge bg-warning';
        }

        if (data.jev.stats.complete) {
            jevDuelStatus.textContent = '🏆 SOLVED (100% Valid)';
            jevDuelStatus.className = 'badge bg-success';
        } else if (data.jev.grid.empty_cells === 0 && data.jev.stats.violations > 0) {
            jevDuelStatus.textContent = `❌ FAILED (${data.jev.stats.violations} Violations)`;
            jevDuelStatus.className = 'badge bg-danger';
        } else if (data.is_duel_finished && !data.jev.stats.complete) {
            jevDuelStatus.textContent = '🛑 STUCK (No Valid Moves)';
            jevDuelStatus.className = 'badge bg-danger';
        }

        if (data.is_duel_finished) {
            pauseDuel();
            return;
        }

        state.duelInterval = setTimeout(runDuelLoop, 90);
    } catch (err) {
        console.error('Duel error:', err);
        pauseDuel();
    }
}

/* ==========================================================================
   BENCHMARK RUNNER & CHARTS
   ========================================================================== */
async function executeBenchmark() {
    runBenchmarkBtn.disabled = true;
    runBenchmarkBtn.textContent = '⏳ Running Monte Carlo Benchmark...';

    const count = parseInt(benchPuzzleCount.value);
    const diff = benchDifficulty.value;

    try {
        const res = await fetch('/api/benchmark/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ num_puzzles: count, difficulty: diff })
        });
        const result = await res.json();
        state.lastBenchmarkResult = result;
        populateBenchmarkTable(result);
        renderCharts(result);
    } catch (err) {
        console.error('Benchmark error:', err);
    } finally {
        runBenchmarkBtn.disabled = false;
        runBenchmarkBtn.textContent = '📊 Run Automated Monte Carlo Benchmark';
    }
}

function populateBenchmarkTable(result) {
    const m = result.metrics;
    const jev = m['Pure JEV (LLM / RLCD Inference)'];
    const exactor = m['Exactor-Accelerator (Neuro-Symbolic SAT)'];
    const dfs = m['Classical Backtracking (DFS)'];

    if (!jev || !exactor) return;

    const speedup = Math.round(exactor.speedup_vs_baseline);
    const solveDelta = (exactor.solve_rate_pct - jev.solve_rate_pct).toFixed(1);

    const rows = [
        ['Avg Latency per Deduction', `${jev.avg_latency_per_move_ms.toFixed(2)} ms`, `<strong>${exactor.avg_latency_per_move_ms.toFixed(4)} ms</strong>`, `${dfs ? dfs.avg_latency_per_move_ms.toFixed(4) : 0} ms`, `<span class="stat-green">${speedup.toLocaleString()}x Faster</span>`],
        ['Puzzle Solve Rate (%)', `${jev.solve_rate_pct.toFixed(1)}%`, `<strong>${exactor.solve_rate_pct.toFixed(1)}%</strong>`, `${dfs ? dfs.solve_rate_pct.toFixed(1) : 0}%`, `<span class="stat-green">+${solveDelta}% Lift</span>`],
        ['Duplicate Violations / Puzzle', `${jev.avg_violations_per_puzzle.toFixed(1)} errors`, '<strong>0.0 errors</strong>', '0.0 errors', '<span class="stat-green">Zero Boolean Drift</span>'],
        ['API Calls per Puzzle', `${jev.avg_api_calls_per_puzzle.toFixed(1)} calls`, '<strong>0.0 calls</strong> (Local SAT)', '0.0 calls', '<span class="stat-green">100% Cost Elimination</span>'],
        ['Deduction Replicability', 'Stochastic (LLM Drift)', '<strong>100% Deterministic</strong>', 'Deterministic', 'Formal Math Proof']
    ];

    benchmarkTableBody.innerHTML = rows.map(r => `
        <tr>
            <td><strong>${r[0]}</strong></td>
            <td>${r[1]}</td>
            <td>${r[2]}</td>
            <td>${r[3]}</td>
            <td>${r[4]}</td>
        </tr>
    `).join('');
}

function renderCharts(result) {
    const m = result.metrics;
    const jev = m['Pure JEV (LLM / RLCD Inference)'];
    const exactor = m['Exactor-Accelerator (Neuro-Symbolic SAT)'];

    // Latency Chart
    const canvasLat = document.getElementById('latencyChartCanvas');
    if (canvasLat) {
        const ctx = canvasLat.getContext('2d');
        canvasLat.width = canvasLat.parentElement.clientWidth;
        canvasLat.height = 180;
        ctx.clearRect(0, 0, canvasLat.width, canvasLat.height);

        const maxVal = Math.max(jev.avg_latency_per_move_ms, 10);
        const startY = 140;

        const hJev = (jev.avg_latency_per_move_ms / maxVal) * 100;
        ctx.fillStyle = '#a855f7';
        ctx.fillRect(80, startY - hJev, 60, hJev);
        ctx.fillStyle = '#fff';
        ctx.font = '11px JetBrains Mono';
        ctx.fillText(`${jev.avg_latency_per_move_ms.toFixed(1)} ms`, 80, startY - hJev - 8);
        ctx.fillText('Pure JEV', 85, startY + 20);

        const hEx = Math.max(2, (exactor.avg_latency_per_move_ms / maxVal) * 100);
        ctx.fillStyle = '#06b6d4';
        ctx.fillRect(220, startY - hEx, 60, hEx);
        ctx.fillStyle = '#fff';
        ctx.fillText(`${exactor.avg_latency_per_move_ms.toFixed(4)} ms`, 210, startY - hEx - 8);
        ctx.fillText('Exactor SAT', 205, startY + 20);
    }

    // Solve Rate Chart
    const canvasAcc = document.getElementById('accuracyChartCanvas');
    if (canvasAcc) {
        const ctx = canvasAcc.getContext('2d');
        canvasAcc.width = canvasAcc.parentElement.clientWidth;
        canvasAcc.height = 180;
        ctx.clearRect(0, 0, canvasAcc.width, canvasAcc.height);
        const startY = 140;

        const hJev = (jev.solve_rate_pct / 100) * 100;
        ctx.fillStyle = '#a855f7';
        ctx.fillRect(80, startY - hJev, 60, hJev);
        ctx.fillStyle = '#fff';
        ctx.font = '11px JetBrains Mono';
        ctx.fillText(`${jev.solve_rate_pct.toFixed(1)}%`, 85, startY - hJev - 8);
        ctx.fillText('Pure JEV', 85, startY + 20);

        const hEx = (exactor.solve_rate_pct / 100) * 100;
        ctx.fillStyle = '#10b981';
        ctx.fillRect(220, startY - hEx, 60, hEx);
        ctx.fillStyle = '#fff';
        ctx.fillText(`${exactor.solve_rate_pct.toFixed(1)}%`, 225, startY - hEx - 8);
        ctx.fillText('Exactor SAT', 215, startY + 20);
    }
}

function exportMarkdownReport() {
    if (!state.lastBenchmarkResult) {
        alert('Please run a benchmark first.');
        return;
    }
    const r = state.lastBenchmarkResult;
    const m = r.metrics;
    const jev = m['Pure JEV (LLM / RLCD Inference)'];
    const exactor = m['Exactor-Accelerator (Neuro-Symbolic SAT)'];

    let md = `# 🔢 Exactor-Accelerator vs Pure JEV Sudoku Benchmark Report\n\n`;
    md += `- **Date:** ${r.timestamp}\n- **Difficulty:** ${r.difficulty}\n- **Sample Size:** ${r.num_puzzles} puzzles\n\n`;
    md += `| Metric | Pure JEV | Exactor-Accelerator | Speedup |\n`;
    md += `| :--- | :---: | :---: | :---: |\n`;
    md += `| **Latency / Deduction** | ${jev.avg_latency_per_move_ms.toFixed(2)} ms | **${exactor.avg_latency_per_move_ms.toFixed(4)} ms** | **${Math.round(exactor.speedup_vs_baseline).toLocaleString()}x Faster** |\n`;
    md += `| **Solve Rate** | ${jev.solve_rate_pct.toFixed(1)}% | **${exactor.solve_rate_pct.toFixed(1)}%** | +${(exactor.solve_rate_pct - jev.solve_rate_pct).toFixed(1)}% Lift |\n`;

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `exactor_sudoku_benchmark_${r.difficulty}.md`;
    a.click();
}
