SERVER_LOG="test-server.log"
python test-server.py >"$SERVER_LOG" 2>&1 &
SERVER_PID=$!

python test-response.py
kill "$SERVER_PID" 2>/dev/null