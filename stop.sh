#!/bin/bash

PID_FILE="$(dirname "$0")/.pids"

if [ ! -f "$PID_FILE" ]; then
  echo "ℹ️  No running voicebot found (.pids not present)."
  exit 0
fi

echo "🛑 Stopping AI Voice Assistant..."

while IFS= read -r pid; do
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" && echo "   Stopped PID $pid"
  else
    echo "   PID $pid already gone"
  fi
done < "$PID_FILE"

rm -f "$PID_FILE"
echo "✅ All processes stopped."
