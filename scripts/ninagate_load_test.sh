#!/bin/bash
LOGFILE="$HOME/nina/ninagate_load_test.log"
echo "Starting 100-prompt load test. Logs in $LOGFILE" > "$LOGFILE"

for i in {1..100}; do
    echo "--- Prompt $i/100 ---" >> "$LOGFILE"
    
    # We query the proxy directly to test the in-memory latency scoring
    # without tearing down the proxy between requests.
    
    curl -s -w "\nHTTP_CODE: %{http_code}\nTIME_TOTAL: %{time_total}s\n" \
      -X POST http://localhost:8080/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer ninagate" \
      -d "{
        \"model\": \"auto\",
        \"messages\": [{\"role\": \"user\", \"content\": \"Reply with just the number $i\"}],
        \"stream\": false
      }" >> "$LOGFILE"
    
    echo "" >> "$LOGFILE"
    
    if [ $i -lt 100 ]; then
        sleep 10
    fi
done

echo "Load test complete." >> "$LOGFILE"
