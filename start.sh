#!/bin/bash

PID_FILE="$(dirname "$0")/.pids"
LOG_DIR="$(dirname "$0")/logs"

# ── Guard: already running? ────────────────────────────────────────────────
if [ -f "$PID_FILE" ]; then
  echo "⚠️  Voicebot appears to be already running (found .pids)."
  echo "   Run ./stop.sh first, or delete .pids if it's stale."
  exit 1
fi

mkdir -p "$LOG_DIR"

# ── Activate virtualenv (auto-create if missing) ─────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
  source "$VENV_DIR/bin/activate"
  echo "📦 Installing dependencies from requirements.txt..."
  pip install -q -r "$SCRIPT_DIR/requirements.txt"
  echo "📦 Downloading LiveKit agent model files..."
  python -m livekit.agents download-files
else
  source "$VENV_DIR/bin/activate"
fi

cd "$SCRIPT_DIR"

echo "🚀 Starting AI Voice Assistant..."

# Start Flask API + frontend
nohup python api.py > "$LOG_DIR/api.log" 2>&1 &
API_PID=$!

# Start LiveKit agent
nohup python agent.py start > "$LOG_DIR/agent.log" 2>&1 &
AGENT_PID=$!

# Save PIDs
echo "$API_PID" > "$PID_FILE"
echo "$AGENT_PID" >> "$PID_FILE"

echo "✅ API (Flask)     → PID $API_PID   | logs/api.log"
echo "✅ Agent (LiveKit) → PID $AGENT_PID  | logs/agent.log"
echo ""
echo "🌐 Open http://localhost:5001 in your browser"
echo "   Run ./stop.sh to shut everything down."
