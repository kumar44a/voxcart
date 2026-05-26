#!/bin/bash
# Kill any orphaned inference subprocesses (multiprocessing.spawn children)
# that may survive if the agent is killed abruptly
pkill -9 -f 'multiprocessing.spawn\|multiprocessing.resource_tracker' 2>/dev/null || true

PID_FILE="$(dirname "$0")/.pids"

if [ ! -f "$PID_FILE" ]; then
  echo "ℹ️  No running voicebot found (.pids not present)."
  exit 0
fi

echo "🛑 Stopping AI Voice Assistant..."

while IFS= read -r pid; do
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    # Kill the entire process tree rooted at this PID (job subprocesses etc.)
    pkill -9 -P "$pid" 2>/dev/null || true
    kill -9 "$pid" && echo "   Stopped PID $pid" || echo "   PID $pid already gone"
  else
    echo "   PID $pid already gone"
  fi
done < "$PID_FILE"

# Kill any remaining voxcart venv Python processes (job pool workers)
pkill -9 -f 'voxcart/venv.*python' 2>/dev/null || true
pkill -9 -f 'voxcart/.*api.py' 2>/dev/null || true
pkill -9 -f 'voxcart/.*agent.py start' 2>/dev/null || true

# Force-kill any process still holding port 5001 or 8081 regardless of how it was launched
lsof -ti:5001 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:8081 2>/dev/null | xargs kill -9 2>/dev/null || true

# Wait for ports to be released before returning
for i in $(seq 1 10); do
  if ! lsof -ti:5001 &>/dev/null && ! lsof -ti:8081 &>/dev/null; then
    break
  fi
  sleep 0.5
done

rm -f "$PID_FILE"
echo "✅ All processes stopped."
