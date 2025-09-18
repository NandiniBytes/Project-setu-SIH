#!/bin/bash

# Project Setu - Quick Manual Demo Setup
# Since your backend is already running!

echo "🏥 Project Setu - Manual Demo Setup"
echo "==================================="
echo ""

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend not detected. Please start it first:"
    echo "   cd project_setu && python3 run_fastapi.py"
    exit 1
fi

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found. Please install ngrok first:"
    echo "1. Go to https://ngrok.com/download"
    echo "2. Download and install ngrok"
    echo "3. Sign up and get your auth token"
    echo "4. Run: ngrok config add-authtoken YOUR_TOKEN"
    exit 1
fi

echo "✅ ngrok found"

# Start ngrok tunnel
echo "🌐 Starting ngrok tunnel for port 8000..."
echo "📝 This will create a public URL for your backend"
echo ""

# Start ngrok in background and capture output
ngrok http 8000 > /dev/null 2>&1 &
NGROK_PID=$!

# Wait for ngrok to start
echo "⏳ Waiting for ngrok to initialize..."
sleep 5

# Get ngrok public URL
NGROK_URL=""
for i in {1..10}; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for tunnel in data['tunnels']:
        if tunnel['proto'] == 'https':
            print(tunnel['public_url'])
            break
except:
    pass
" 2>/dev/null)
    
    if [ ! -z "$NGROK_URL" ]; then
        break
    fi
    echo "   Attempt $i/10 - waiting for ngrok..."
    sleep 2
done

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to get ngrok URL"
    echo "💡 Try manually:"
    echo "1. Open http://localhost:4040 in browser"
    echo "2. Copy the https:// URL"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

echo "✅ ngrok tunnel created!"
echo ""

# Update Streamlit secrets
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
BACKEND_URL = "$NGROK_URL"
EOF

echo "✅ Updated Streamlit configuration"
echo ""

# Display results
echo "🎉 Demo Setup Complete!"
echo "======================"
echo ""
echo "🔗 Your Public URLs:"
echo "📡 Backend API: $NGROK_URL"
echo "📖 API Documentation: $NGROK_URL/docs"
echo "🔍 Health Check: $NGROK_URL/health"
echo ""
echo "📋 For Your PPT:"
echo "==============="
echo "Backend URL: $NGROK_URL"
echo ""
echo "🌐 For Streamlit Cloud:"
echo "1. Go to https://share.streamlit.io/"
echo "2. Connect your GitHub repo"
echo "3. Set file: project_setu/streamlit_beautiful.py"
echo "4. Deploy!"
echo ""
echo "🎮 Demo Credentials:"
echo "ABHA ID: 12-3456-7890-1234"
echo "Password: testpassword"
echo ""
echo "⚠️  Keep this terminal open to maintain ngrok tunnel!"
echo "Press Ctrl+C to stop"

# Keep running
trap 'echo ""; echo "🛑 Stopping ngrok tunnel..."; kill $NGROK_PID 2>/dev/null || true; exit' INT
echo ""
echo "✨ Your demo is live! Test the API: curl $NGROK_URL/health"
echo ""

# Wait indefinitely
while true; do
    sleep 30
    # Check if ngrok is still running
    if ! kill -0 $NGROK_PID 2>/dev/null; then
        echo "❌ ngrok tunnel stopped unexpectedly"
        break
    fi
done
