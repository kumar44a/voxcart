#!/bin/bash
# healthcheck.sh — VoxCart pre-flight & post-start health checker
# Run before a demo to verify everything is ready.

PASS=0
FAIL=0

ok()   { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }
info() { echo "  ℹ️  $1"; }
section() { echo; echo "── $1 ──"; }

# ─── 1. ENVIRONMENT ───────────────────────────────────────────────────────────
section "Environment"

if [ -f .env ]; then
  ok ".env file present"
  MISSING_KEYS=()
  for key in LIVEKIT_URL LIVEKIT_API_KEY LIVEKIT_API_SECRET OPENAI_API_KEY CARTESIA_API_KEY; do
    if ! grep -q "^${key}=" .env 2>/dev/null; then
      MISSING_KEYS+=("$key")
    fi
  done
  if [ ${#MISSING_KEYS[@]} -eq 0 ]; then
    ok "All 5 required .env keys present"
  else
    fail "Missing .env keys: ${MISSING_KEYS[*]}"
  fi
else
  fail ".env file NOT found — agent cannot start"
fi

if [ -f venv/bin/activate ]; then
  ok "Python venv exists at venv/"
else
  fail "Python venv NOT found — run: python3 -m venv venv && pip install -r requirements.txt"
fi

# ─── 2. PROCESS STATUS ────────────────────────────────────────────────────────
section "Process Status"

if [ -f .pids ]; then
  PIDS=$(cat .pids)
  ALL_ALIVE=true
  for pid in $PIDS; do
    if kill -0 "$pid" 2>/dev/null; then
      info "PID $pid alive"
    else
      fail "PID $pid in .pids is NOT running (stale .pids — run ./stop.sh then ./start.sh)"
      ALL_ALIVE=false
    fi
  done
  $ALL_ALIVE && ok ".pids file present and all PIDs alive"
else
  fail ".pids not found — voicebot is NOT running (run ./start.sh)"
fi

ORPHANS=$(pgrep -f "multiprocessing.spawn\|multiprocessing.resource_tracker" 2>/dev/null | wc -l | tr -d ' ')
if [ "$ORPHANS" -eq 0 ]; then
  ok "No orphaned inference subprocesses"
else
  fail "$ORPHANS orphaned inference subprocess(es) detected — run ./stop.sh to clean up"
fi

# ─── 3. FLASK API ─────────────────────────────────────────────────────────────
section "Flask API (port 5001)"

if lsof -iTCP:5001 -sTCP:LISTEN -n -P &>/dev/null; then
  ok "Port 5001 is LISTENING"
else
  fail "Port 5001 is NOT listening — Flask API may not have started"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://localhost:5001/ 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
  ok "GET / returned HTTP 200"
else
  fail "GET / returned HTTP $HTTP_CODE (expected 200)"
fi

TOKEN_RESP=$(curl -s --max-time 5 "http://localhost:5001/getToken?name=healthcheck" 2>/dev/null)
if echo "$TOKEN_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'token' in d and len(d['token'])>20" 2>/dev/null; then
  ok "/getToken returns a valid JWT"
else
  fail "/getToken did not return a valid token — response: ${TOKEN_RESP:0:80}"
fi

# ─── 4. LIVEKIT AGENT ─────────────────────────────────────────────────────────
section "LiveKit Agent"

AGENT_LOG="logs/agent.log"
if [ -f "$AGENT_LOG" ] && [ -s "$AGENT_LOG" ]; then
  ok "logs/agent.log exists and is non-empty"

  if grep -q '"registered worker"' "$AGENT_LOG" 2>/dev/null; then
    WORKER_LINE=$(grep '"registered worker"' "$AGENT_LOG" | tail -1)
    REGION=$(echo "$WORKER_LINE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('region','?'))" 2>/dev/null)
    ok "Agent registered with LiveKit Cloud (region: $REGION)"
  elif grep -q '"worker failed"' "$AGENT_LOG" 2>/dev/null; then
    FAIL_MSG=$(grep '"worker failed"' "$AGENT_LOG" | tail -1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error','?'))" 2>/dev/null)
    fail "Agent log shows 'worker failed': $FAIL_MSG"
  else
    info "Agent log present but 'registered worker' not yet seen — may still be starting"
  fi

  if grep -q '"starting inference executor"' "$AGENT_LOG" 2>/dev/null; then
    fail "WARN: 'starting inference executor' found in log — MultilingualModel may be active (slow startup risk)"
  else
    ok "No inference executor subprocess (fast startup mode)"
  fi
else
  fail "logs/agent.log is missing or empty"
fi

# ─── 5. MODEL CACHE ───────────────────────────────────────────────────────────
section "Model Cache"

TURN_CACHE=~/.cache/huggingface/hub/models--livekit--turn-detector
if [ -d "$TURN_CACHE" ]; then
  SNAPSHOTS=$(ls "$TURN_CACHE/snapshots/" 2>/dev/null | wc -l | tr -d ' ')
  ok "HuggingFace turn-detector cache present ($SNAPSHOTS snapshot(s))"
else
  info "HuggingFace turn-detector cache absent — OK if MultilingualModel is not in use"
fi

SILERO_ONNX=$(find venv/lib -name "silero_vad.onnx" 2>/dev/null | head -1)
if [ -n "$SILERO_ONNX" ]; then
  ok "Silero VAD model present: $SILERO_ONNX"
else
  fail "Silero VAD model (silero_vad.onnx) NOT found in venv"
fi

# ─── SUMMARY ──────────────────────────────────────────────────────────────────
TOTAL=$((PASS + FAIL))
echo
echo "══════════════════════════════"
if [ $FAIL -eq 0 ]; then
  echo "  ✅ ALL $TOTAL checks passed — VoxCart is healthy!"
else
  echo "  ⚠️  $PASS/$TOTAL checks passed — $FAIL issue(s) need attention"
fi
echo "══════════════════════════════"
echo
exit $FAIL
