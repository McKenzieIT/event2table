#!/bin/bash
# Restart Flask Server with GraphQL Support

echo "🔄 Restarting Flask server..."

# Kill existing Flask processes
PIDS=$(ps aux | grep 'python.*web_app' | grep -v grep | awk '{print $2}')
if [ -n "$PIDS" ]; then
    echo "Killing old Flask processes: $PIDS"
    kill -9 $PIDS 2>/dev/null
    sleep 2
fi

# Start new Flask server
echo "Starting Flask server..."
cd /Users/mckenzie/Documents/event2table

# Start in background
nohup python3 web_app.py > /tmp/flask.log 2>&1 &
FLASK_PID=$!

echo "Flask server started (PID: $FLASK_PID)"
echo "Logs: /tmp/flask.log"

# Wait for server to start
sleep 3

# Verify GraphQL endpoint
echo ""
echo "🔍 Verifying GraphQL endpoint..."
curl -s -X POST http://127.0.0.1:5001/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}' | jq .

echo ""
echo "✅ Flask server restarted successfully!"
echo ""
echo "GraphQL endpoint available at: http://127.0.0.1:5001/api/graphql"
echo "GraphiQL IDE available at: http://127.0.0.1:5001/api/graphql?graphiql"
